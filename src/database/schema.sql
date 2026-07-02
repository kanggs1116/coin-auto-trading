CREATE TABLE IF NOT EXISTS markets (
    id BIGSERIAL PRIMARY KEY,

    market VARCHAR(20) NOT NULL UNIQUE,

    korean_name VARCHAR(100) NOT NULL,

    english_name VARCHAR(100) NOT NULL,

    market_warning VARCHAR(20) NOT NULL DEFAULT 'NONE',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candles (
    id BIGSERIAL PRIMARY KEY,

    market VARCHAR(20) NOT NULL,

    candle_type VARCHAR(20) NOT NULL,

    unit INTEGER,

    candle_date_time_utc TIMESTAMP NOT NULL,

    candle_date_time_kst TIMESTAMP NOT NULL,

    opening_price NUMERIC(20, 8) NOT NULL,

    high_price NUMERIC(20, 8) NOT NULL,

    low_price NUMERIC(20, 8) NOT NULL,

    trade_price NUMERIC(20, 8) NOT NULL,

    candle_acc_trade_price NUMERIC(30, 8) NOT NULL,

    candle_acc_trade_volume NUMERIC(30, 12) NOT NULL,

    timestamp_ms BIGINT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_candles_market_type_unit_time
        UNIQUE (market, candle_type, unit, candle_date_time_utc)
);