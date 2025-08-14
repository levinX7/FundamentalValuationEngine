USE `stocks`;

-- parent
DROP TABLE IF EXISTS `forecast`,`risk`,`fundamental`,`basic_info`;
CREATE TABLE `basic_info` (
  `ticker`               VARCHAR(16) NOT NULL,
  `current_market_cap_b` FLOAT,
  `current_price`        FLOAT,
  `sector`               VARCHAR(64),
  PRIMARY KEY (`ticker`)
) ENGINE=InnoDB;

-- fundamental (1:1 to basic_info via ticker)
CREATE TABLE `fundamental` (
  `ticker`                 VARCHAR(16) NOT NULL,
  `fundamental_id`         INT NOT NULL AUTO_INCREMENT,
  `mutliples_market_cap_b` FLOAT,
  `ddm_market_cap_b`       FLOAT,
  `dcf_market_cap_b`       FLOAT,
  `median_market_cap_b`    FLOAT,
  `buy?`                   BOOLEAN, -- TINYINT
  PRIMARY KEY (`fundamental_id`),
  UNIQUE KEY `uq_fundamental_ticker` (`ticker`),
  CONSTRAINT `fk_fundamental_basic_info`
    FOREIGN KEY (`ticker`) REFERENCES `basic_info` (`ticker`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- risk (1:1)
CREATE TABLE `risk` (
  `ticker`                 VARCHAR(16) NOT NULL,
  `risk_id`                INT NOT NULL AUTO_INCREMENT,
  `cumulative_return`      FLOAT,
  `annualized_return`      FLOAT,
  `annualized_volatility`  FLOAT,
  `sharpe_ratio`           FLOAT,
  PRIMARY KEY (`risk_id`),
  UNIQUE KEY `uq_risk_ticker` (`ticker`),
  CONSTRAINT `fk_risk_basic_info`
    FOREIGN KEY (`ticker`) REFERENCES `basic_info` (`ticker`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- forecast (1:1)
CREATE TABLE `forecast` (
  `ticker`                 VARCHAR(16) NOT NULL,
  `forecast_id`            INT NOT NULL AUTO_INCREMENT,
  `forecast_price_30d`     FLOAT,
  `forecast_market_cap_b`  FLOAT,
  `forecast_change_%`      FLOAT,
  PRIMARY KEY (`forecast_id`),
  UNIQUE KEY `uq_forecast_ticker` (`ticker`),
  CONSTRAINT `fk_forecast_basic_info`
    FOREIGN KEY (`ticker`) REFERENCES `basic_info` (`ticker`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;