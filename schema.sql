

-- coin_list definition
DROP TABLE IF EXISTS coin_list;
CREATE TABLE coin_list (
	source TEXT NOT NULL, 
	id TEXT NOT NULL, 
	symbol TEXT, 
	name TEXT, 
	date DATETIME NOT NULL, 
	PRIMARY KEY (source, id)
);
CREATE INDEX ix_coin_list_source ON coin_list (source);
CREATE INDEX ix_coin_list_id ON coin_list (id);
CREATE INDEX ix_coin_list_name ON coin_list (name);
CREATE INDEX ix_coin_list_symbol ON coin_list (symbol);
CREATE INDEX ix_coin_list_date ON coin_list (date);


-- coin_list_detail definition
DROP TABLE IF EXISTS coin_list_detail;
CREATE TABLE coin_list_detail (
	source TEXT NOT NULL, 
	base_currency TEXT NOT NULL, 
	id TEXT NOT NULL, 
	num_id BIGINT, -- numeric ID for CoinGecko
	symbol TEXT, 
	name TEXT, 
	image TEXT, 
	current_price FLOAT, 
	market_cap FLOAT, 
	market_cap_rank UNSIGNED BIGINT, 
	fully_diluted_valuation FLOAT, 
	total_volume FLOAT, 
	high_24h FLOAT, 
	low_24h FLOAT, 
	high_7d FLOAT, 
	low_7d FLOAT, 
	price_change_24h FLOAT, 
	price_change_percentage_24h FLOAT, 
	market_cap_change_24h FLOAT, 
	market_cap_change_percentage_24h FLOAT, 
	circulating_supply FLOAT, 
	total_supply FLOAT, 
	max_supply FLOAT, 
	ath FLOAT, 
	ath_change_percentage FLOAT, 
	ath_date DATETIME, 
	atl FLOAT, 
	atl_change_percentage FLOAT, 
	atl_date DATETIME, 
	roi TEXT, 
	last_updated DATETIME, 
	price_change_percentage_1h_in_currency FLOAT, 
	price_change_percentage_24h_in_currency FLOAT, 
	price_change_percentage_7d_in_currency FLOAT, 
	sparkline_in_7d TEXT, -- associative array with key 'price' containing an array of n prices
	sparkline_unicode_7d TEXT,
	sparkline_unicode_24h TEXT,
	date DATETIME NOT NULL, 
	page_num BIGINT, 
	PRIMARY KEY (source, base_currency, id)
);

CREATE INDEX ix_coin_list_detail_source ON coin_list_detail (source);
CREATE INDEX ix_coin_list_detail_base_currency ON coin_list_detail (base_currency);
CREATE INDEX ix_coin_list_detail_id ON coin_list_detail (id);
CREATE INDEX ix_coin_list_detail_name ON coin_list_detail (name);
CREATE INDEX ix_coin_list_detail_symbol ON coin_list_detail (symbol);
CREATE INDEX ix_coin_list_detail_date ON coin_list_detail (date);

-- logo_list definition
DROP TABLE IF EXISTS logo_list;
CREATE TABLE logo_list (
	source TEXT NOT NULL, 
	title_text TEXT NOT NULL, 
	link TEXT NOT NULL,
	name TEXT NOT NULL, 
	symbol TEXT NOT NULL, 
	priority INT NOT NULL,
	logo_contents TEXT,
	file_type TEXT NOT NULL,

	date DATETIME NOT NULL, 
	PRIMARY KEY (source, name, symbol)
);
CREATE INDEX ix_logo_list_source ON logo_list (source);
CREATE INDEX ix_logo_list_name ON logo_list (name);
CREATE INDEX ix_logo_list_symbol ON logo_list (symbol);
CREATE INDEX ix_logo_list_date ON logo_list (date);
