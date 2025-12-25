function MetricsCard({ title, value }) {
  return (
    <div className="card">
      <h4>{title}</h4>
      <p style={{ fontSize: "22px", fontWeight: "bold" }}>{value}</p>
    </div>
  );
}

export default MetricsCard;
