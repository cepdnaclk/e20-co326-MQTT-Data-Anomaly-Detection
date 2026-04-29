export default function AnomalyFeed({ anomalies }) {
  return (
    <div className="event-list">
      {anomalies.length === 0 && (
        <div className="empty-events">
          No protection events
        </div>
      )}
      {anomalies.map((event, index) => (
        <div
          key={`${event.time}-${index}`}
          className={`anomaly-item ${event.level === "critical" ? "critical" : "warning"}`}
        >
          <span className="event-marker">{event.level === "critical" ? "!" : "i"}</span>
          <div>
            <div className="event-title">
              {event.level.toUpperCase()} - {event.sensor}
            </div>
            <div className="event-copy">
              {event.msg} - {event.time}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
