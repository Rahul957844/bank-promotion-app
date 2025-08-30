import { useState } from "react";

export default function Home() {
  const [accountId, setAccountId] = useState("");
  const [introducerId, setIntroducerId] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("https://bank-promotion-app.onrender.com/accounts/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          account_id: parseInt(accountId),
          introducer_id: introducerId ? parseInt(introducerId) : null,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        console.error("Server Error:", res.status, errText);
        return;
      }

      const data = await res.json();
      console.log("✅ Response from backend:", data);
      setResult(data);
    } catch (error) {
      console.error("❌ Fetch failed:", error);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>New Bank Account</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          placeholder="Account ID"
          value={accountId}
          onChange={(e) => setAccountId(e.target.value)}
        /><br/>
        <input
          type="number"
          placeholder="Introducer ID"
          value={introducerId}
          onChange={(e) => setIntroducerId(e.target.value)}
        /><br/>
        <button type="submit">Submit</button>
      </form>

      {result && (
        <div>
          <p>AccountID: {result.account_id}</p>
          <p>IntroducerID: {result.introducer_id}</p>
          <p>BeneficiaryID: {result.beneficiary_id}</p>
        </div>
      )}
    </div>
  );
}
