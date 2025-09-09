# app/services/eval_service.py
from sqlalchemy.orm import Session
from app.models.eval import EvalCase, EvalResult
from app.schemas.eval import EvalCaseCreate, EvalResultRead, EvalMetrics
from typing import List
import time
import asyncio
from app.core.sse import sse  # ✅ SSE manager
import logging


class EvalService:

    @staticmethod
    async def run_eval_case(db: Session, case_data: EvalCaseCreate) -> EvalResultRead:
        """
        Simulate running an evaluation case asynchronously.
        """
        def _run():
            eval_case = EvalCase(**case_data.dict())
            db.add(eval_case)
            db.commit()
            db.refresh(eval_case)

            start_time = time.time()
            passed = 1 if eval_case.input_data == eval_case.expected_output else 0
            execution_time = time.time() - start_time

            result = EvalResult(
                eval_case_id=eval_case.id,
                actual_output=eval_case.input_data,
                passed=passed,
                execution_time=execution_time
            )

            db.add(result)
            db.commit()
            db.refresh(result)
            return result

        result = await asyncio.to_thread(_run)

        # 🔔 SSE event for new evaluation result
        try:
            if sse:
                await sse.publish(
                    {
                        "event": "eval_case_completed",
                        "eval_case_id": result.eval_case_id,
                        "passed": result.passed,
                        "execution_time": result.execution_time
                    },
                    type="eval"
                )
        except Exception as e:
            logging.error(f"[SSE Error] Could not publish eval_case_completed: {e}")

        return EvalResultRead.from_orm(result)

    @staticmethod
    async def get_metrics(db: Session) -> EvalMetrics:
        def _metrics():
            total = db.query(EvalCase).count()
            passed = db.query(EvalResult).filter(EvalResult.passed == 1).count()
            failed = db.query(EvalResult).filter(EvalResult.passed == 0).count()
            pass_rate = (passed / total) * 100 if total > 0 else 0
            return EvalMetrics(
                total_cases=total,
                passed_cases=passed,
                failed_cases=failed,
                pass_rate=pass_rate
            )

        metrics = await asyncio.to_thread(_metrics)

        # 🔔 SSE event for metrics update
        try:
            if sse:
                await sse.publish(
                    {
                        "event": "eval_metrics_updated",
                        "metrics": metrics.dict()
                    },
                    type="eval"
                )
        except Exception as e:
            logging.error(f"[SSE Error] Could not publish eval_metrics_updated: {e}")

        return metrics

    @staticmethod
    async def get_all_results(db: Session) -> List[EvalResultRead]:
        def _all_results():
            results = db.query(EvalResult).all()
            return [EvalResultRead.from_orm(r) for r in results]

        results = await asyncio.to_thread(_all_results)

        # 🔔 SSE event for results fetch
        try:
            if sse:
                await sse.publish(
                    {
                        "event": "eval_results_fetched",
                        "count": len(results)
                    },
                    type="eval"
                )
        except Exception as e:
            logging.error(f"[SSE Error] Could not publish eval_results_fetched: {e}")

        return results
