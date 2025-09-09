import React, { useEffect, useState } from "react";
import client from "../../ api/client";

interface Props {
  customerId: string;
}

const InsightsCharts: React.FC<Props> = ({ customerId }) => {
  const [categories, setCategories] = useState<{ category: string; spend: number }[]>([]);
  const [merchants, setMerchants] = useState<{ merchant: string; spend: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!customerId) return;
    setLoading(true);
    setError(null);

    const fetchInsights = async () => {
      try {
        // Fetch categories (object → array)
       const categoriesRes = await client.get(`/insights/${customerId}/categories`);
const catData = categoriesRes.data || {};
const catArray = Object.entries(catData).map(([category, spend]) => ({
  category,
  spend: Number(spend), // 👈 explicitly cast to number
}));
setCategories(catArray);

        // Fetch top merchants (array → objects)
        const merchantsRes = await client.get(`/insights/${customerId}/top-merchants`);
        const merchData = merchantsRes.data || [];
        const merchArray = merchData.map(([merchant, spend]: [string, number]) => ({
          merchant,
          spend,
        }));
        setMerchants(merchArray);
      } catch (err: any) {
        console.error("Error fetching insights:", err);
        setError("Failed to load insights");
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, [customerId]);

  if (loading) return <p>Loading insights...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div style={{ display: "flex", gap: "2rem" }}>
      {/* Spend by Category */}
      <div style={{ flex: 1 }}>
        <h3>Spend by Category</h3>
        {categories.length > 0 ? (
         <ul>
  {categories.map((c, idx) => (
    <li key={idx}>
      {c.category}: {(c.spend ?? 0).toFixed(2)}
    </li>
  ))}
</ul>
        ) : (
          <p>No category data available</p>
        )}
      </div>

      {/* Top Merchants */}
      <div style={{ flex: 1 }}>
        <h3>Top Merchants</h3>
        {merchants.length > 0 ? (
         <ul>
  {merchants.map((m, idx) => (
    <li key={idx}>
      {m.merchant}: {(m.spend ?? 0).toFixed(2)}
    </li>
  ))}
</ul>
        ) : (
          <p>No merchant data available</p>
        )}
      </div>
    </div>
  );
};

export default InsightsCharts;
