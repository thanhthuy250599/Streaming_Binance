CREATE TABLE IF NOT EXISTS kpi_symbol_1m (
  window_start timestamptz NOT NULL,
  window_end   timestamptz NOT NULL,
  symbol       text        NOT NULL,
  trades       int         NOT NULL,
  avg_price    double precision,
  vwap         double precision,
  volume       double precision,
  volatility   double precision,
  anomaly      boolean,
  inserted_at  timestamptz DEFAULT now(),
  PRIMARY KEY (window_start, symbol)
);

CREATE INDEX IF NOT EXISTS kpi_symbol_1m_symbol_time_idx
  ON kpi_symbol_1m(symbol, window_start);