import React from "react";

interface StatusCardProps {
  name: string;
  state: string;
  failures: number;
  lastFailure: string | null;
}

const StatusCard: React.FC<StatusCardProps> = ({ name, state, failures, lastFailure }) => {
  const stateColor =
    state === "closed" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700";

  return (
    <div className="bg-white shadow rounded-xl p-4 w-56">
      <h3 className="text-lg font-semibold capitalize">{name.replace("_", " ")}</h3>
      <span
        className={`inline-block px-3 py-1 mt-2 text-sm rounded-full ${stateColor}`}
      >
        {state}
      </span>
      <p className="text-sm text-gray-600 mt-2">Failures: {failures}</p>
      <p className="text-sm text-gray-600">
        Last Failure: {lastFailure ? lastFailure : "None"}
      </p>
    </div>
  );
};

export default StatusCard;
