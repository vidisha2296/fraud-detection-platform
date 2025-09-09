# from typing import Dict, List, Any
# from app.agents.base_agent import BaseAgent, AgentResponse
# from app.agents.insights_agent import InsightsAgent
# from app.agents.fraud_agent import FraudAgent
# from app.agents.kb_agent import KBAgent
# from app.agents.compliance_agent import ComplianceAgent
# from app.models.agent_models import CustomerProfile, FraudAssessment, ActionProposal

# class Orchestrator(BaseAgent):
#     def __init__(self):
#         super().__init__("orchestrator")
#         self.insights_agent = InsightsAgent()
#         self.fraud_agent = FraudAgent()
#         self.kb_agent = KBAgent()
#         self.compliance_agent = ComplianceAgent()
    
#     async def execute_plan(
#         self,
#         customer_id: str,
#         transaction_data: Dict[str, Any],
#         plan: List[str] = None
#     ) -> Dict[str, Any]:
#         """Execute the agent plan with 5s total timeout"""
        
#         if plan is None:
#             plan = [
#                 "getProfile", "getRecentTransactions", "riskSignals",
#                 "kbLookup", "decide", "proposeAction"
#             ]
        
#         context = {
#             "customer_id": customer_id,
#             "transaction": transaction_data,
#             "results": {}
#         }
        
#         try:
#             # Execute entire plan within 5 second budget
#             result = await asyncio.wait_for(
#                 self._execute_plan_steps(plan, context),
#                 timeout=5.0
#             )
#             return result
            
#         except asyncio.TimeoutError:
#             return {
#                 "success": False,
#                 "error": "Total plan execution timeout (5s exceeded)",
#                 "partial_results": context["results"]
#             }
    
#     async def _execute_plan_steps(self, plan: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
#         """Execute each step of the plan"""
        
#         for step in plan:
#             step_result = await self._execute_step(step, context)
            
#             if not step_result.success:
#                 return {
#                     "success": False,
#                     "error": f"Step {step} failed: {step_result.error}",
#                     "results": context["results"]
#                 }
            
#             context["results"][step] = step_result.data
        
#         # Apply final compliance check
#         compliance_result = await self.compliance_agent.check_action(
#             context["results"].get("proposeAction")
#         )
        
#         if not compliance_result.success:
#             return {
#                 "success": False,
#                 "error": f"Compliance check failed: {compliance_result.error}",
#                 "results": context["results"]
#             }
        
#         return {
#             "success": True,
#             "results": context["results"],
#             "final_action": compliance_result.data
#         }
    
#     async def _execute_step(self, step: str, context: Dict[str, Any]) -> AgentResponse:
#         """Execute individual plan step"""
        
#         if step == "getProfile":
#             return await self.insights_agent.get_customer_profile(
#                 context["customer_id"]
#             )
        
#         elif step == "getRecentTransactions":
#             return await self.insights_agent.get_recent_transactions(
#                 context["customer_id"], hours=24
#             )
        
#         elif step == "riskSignals":
#             return await self.fraud_agent.assess_risk(
#                 context["customer_id"],
#                 context["transaction"],
#                 context["results"].get("getRecentTransactions", [])
#             )
        
#         elif step == "kbLookup":
#             risk_signals = context["results"].get("riskSignals", {})
#             return await self.kb_agent.lookup_relevant_rules(
#                 context["customer_id"],
#                 context["transaction"],
#                 risk_signals.get("risk_score", 0)
#             )
        
#         elif step == "decide":
#             return await self.fraud_agent.make_decision(
#                 context["results"].get("riskSignals", {}),
#                 context["results"].get("kbLookup", [])
#             )
        
#         elif step == "proposeAction":
#             decision = context["results"].get("decide", {})
#             return await self.fraud_agent.propose_action(
#                 decision,
#                 context["transaction"]
#             )
        
#         else:
#             return AgentResponse(
#                 success=False,
#                 error=f"Unknown plan step: {step}"
#             )


from typing import Dict, List, Any
from app.agents.base_agent import BaseAgent, AgentResponse
from app.agents.insights_agent import InsightsAgent
from app.agents.fraud_agent import FraudAgent
from app.agents.kb_agent import KBAgent
from app.agents.compliance_agent import ComplianceAgent
from app.models.agent_models import CustomerProfile, FraudAssessment, ActionProposal
from app.core.circuit_breaker import CircuitBreaker


class Orchestrator(BaseAgent):
    def __init__(self):
        super().__init__(name="Orchestrator")
        self.insights_agent = InsightsAgent()
        self.fraud_agent = FraudAgent()
        self.kb_agent = KBAgent()
        self.compliance_agent = ComplianceAgent()
        self.circuit_breaker = CircuitBreaker(name="orchestrator")

    async def run(self, query: str, customer: CustomerProfile) -> AgentResponse:
        if not self.circuit_breaker.allow_request():
            return AgentResponse(success=False, error="Orchestrator unavailable (circuit open)")

        context = {
            "query": query,
            "customer": customer,
            "results": {}
        }

        try:
            plan = await self._make_plan(query, customer)
            result = await self._execute_plan_steps(plan, context)

            # If successful → reset circuit breaker
            if result.get("success", False):
                self.circuit_breaker.on_success()

            return AgentResponse(success=True, data=result)
        except Exception as e:
            self.circuit_breaker.on_failure()
            return AgentResponse(success=False, error=str(e))

    async def _make_plan(self, query: str, customer: CustomerProfile) -> List[str]:
        """
        Very basic planner: decide which agents to call based on query keywords.
        In production, this could use an LLM-based planner.
        """
        plan = []
        if "fraud" in query.lower() or "charge" in query.lower():
            plan.append("fraud")
        if "insight" in query.lower() or "spend" in query.lower():
            plan.append("insights")
        if "compliance" in query.lower() or "kyc" in query.lower():
            plan.append("compliance")
        if "how" in query.lower() or "what" in query.lower():
            plan.append("kb")
        return plan

    async def _execute_plan_steps(self, plan: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        for step in plan:
            try:
                step_result = await self._execute_with_retries(step, context)
            except Exception as e:
                context["failed_step"] = step
                self.circuit_breaker.on_failure()
                return {
                    "success": False,
                    "error": f"Step {step} failed: {str(e)}",
                    "results": context["results"],
                    "failed_step": step
                }

            if not step_result.success:
                context["failed_step"] = step
                self.circuit_breaker.on_failure()
                return {
                    "success": False,
                    "error": f"Step {step} failed: {step_result.error}",
                    "results": context["results"],
                    "failed_step": step
                }

            # Store step results
            context["results"][step] = step_result.data

        return {
            "success": True,
            "results": context["results"]
        }

    async def _execute_with_retries(self, step: str, context: Dict[str, Any], retries: int = 2) -> AgentResponse:
        for attempt in range(retries + 1):
            try:
                if step == "fraud":
                    return await self.fraud_agent.run(context["query"], context["customer"])
                elif step == "insights":
                    return await self.insights_agent.run(context["query"], context["customer"])
                elif step == "kb":
                    return await self.kb_agent.run(context["query"], context["customer"])
                elif step == "compliance":
                    return await self.compliance_agent.run(context["query"], context["customer"])
                else:
                    raise ValueError(f"Unknown step: {step}")
            except Exception as e:
                if attempt == retries:
                    raise e
                continue
