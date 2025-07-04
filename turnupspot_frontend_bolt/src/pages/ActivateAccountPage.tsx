import React, { useEffect, useState, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { get } from "../api";

const ActivateAccountPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<"pending" | "success" | "error">(
    "pending"
  );
  const navigate = useNavigate();
  const called = useRef(false);

  useEffect(() => {
    const token = searchParams.get("token");
    if (!token || called.current) {
      return;
    }
    called.current = true;
    get(`/auth/activate?token=${token}`)
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [searchParams]);

  return (
    <div className="max-w-md mx-auto mt-20 p-8 bg-white rounded shadow text-center">
      {status === "pending" && <p>Activating your account...</p>}
      {status === "success" && (
        <>
          <h2 className="text-2xl font-bold mb-4">Account Activated!</h2>
          <p className="mb-4">You can now sign in to your account.</p>
          <button
            className="bg-indigo-600 text-white px-4 py-2 rounded"
            onClick={() => navigate("/signin")}
          >
            Go to Sign In
          </button>
        </>
      )}
      {status === "error" && (
        <>
          <h2 className="text-2xl font-bold mb-4 text-red-600">
            Activation Failed
          </h2>
          <p className="mb-4">The activation link is invalid or expired.</p>
        </>
      )}
    </div>
  );
};

export default ActivateAccountPage;
