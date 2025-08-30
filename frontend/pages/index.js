import { useState } from "react";

export default function Home() {
  const [accountId, setAccountId] = useState("");
  const [introducerId, setIntroducerId] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("https://bank-promotion-app.onrender.com/accounts/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      account_id: parseInt(accountId),
      introducer_id: introducerId ? parseInt(introducerId) : null
    }),
});

    const data = await res.json();
    setResult(data);
  };

  return (
    <div style={{padding:20}}>
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
          <p>AccountID: {result.AccountID}</p>
          <p>IntroducerID: {result.IntroducerID}</p>
          <p>BeneficiaryID: {result.BeneficiaryID}</p>
        </div>
      )}
    </div>
  );
            }
