CREATE TABLE FROM_CONFIG(
   TRANSPORT_ID         VARCHAR(10),
   TRANSPORT_PASSWORD   VARCHAR(45),
   PARTY_ID             VARCHAR(10) NOT NULL,
   PARTY_DESCRIPTION    VARCHAR(200),
   ROUTING_ID           VARCHAR(39),
   ROUTING_DESCRIPTION  VARCHAR(200),
   SIGN_ID              VARCHAR(4),
   SUBSTITUTE_PARTY_ID  VARCHAR(10),
   PRIMARY KEY (PARTY_ID),
   KEY FROM_CONFIG_INDEX1 (SUBSTITUTE_PARTY_ID)
   
) ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE SCHEDULE_CONFIG(
   TASK                 VARCHAR(30) NOT NULL,
   ENABLE               VARCHAR(1),
   SCHEDULE_TYPE        VARCHAR(10),
   SCHEDULE_WEEK        VARCHAR(15),
   SCHEDULE_TIME        VARCHAR(50),
   SCHEDULE_PERIOD      VARCHAR(10),
   SCHEDULE_RANGE       VARCHAR(15),
   PRIMARY KEY (TASK)
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE SIGN_CONFIG (
  SIGN_ID VARCHAR(4) NOT NULL,
  SIGN_TYPE VARCHAR(10)  DEFAULT NULL,
  PFX_PATH VARCHAR(100)  DEFAULT NULL,
  SIGN_PASSWORD VARCHAR(60)  DEFAULT NULL,
  PRIMARY KEY (SIGN_ID)
) ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TASK_CONFIG(
   CATEGORY_TYPE        VARCHAR(5) NOT NULL,
   PROCESS_TYPE         VARCHAR(10) NOT NULL,
   TASK                 VARCHAR(30) NOT NULL,
   SRC_PATH             VARCHAR(200),
   TARGET_PATH          VARCHAR(200),
   FILE_FORMAT          VARCHAR(20),
   VERSION              VARCHAR(5),
   ENCODING             VARCHAR(15),
   TRANS_CHINESE_DATE   VARCHAR(1),
   PRIMARY KEY (CATEGORY_TYPE, PROCESS_TYPE, TASK)
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TO_CONFIG(
   PARTY_ID             VARCHAR(10) NOT NULL,
   PARTY_DESCRIPTION    VARCHAR(200),
   ROUTING_ID           VARCHAR(39),
   ROUTING_DESCRIPTION  VARCHAR(200),
   FROM_PARTY_ID        VARCHAR(10),
   PRIMARY KEY (FROM_PARTY_ID, PARTY_ID)
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_MESSAGE_LOG (
  SEQNO VARCHAR(8) NOT NULL,
  SUBSEQNO VARCHAR(5) NOT NULL,
  UUID VARCHAR(40) DEFAULT NULL,
  MESSAGE_TYPE VARCHAR(10) DEFAULT NULL,
  CATEGORY_TYPE VARCHAR(5) DEFAULT NULL,
  PROCESS_TYPE VARCHAR(10) DEFAULT NULL,
  FROM_PARTY_ID VARCHAR(10) DEFAULT NULL,
  TO_PARTY_ID VARCHAR(10) DEFAULT NULL,
  MESSAGE_DTS VARCHAR(17) DEFAULT NULL,
  CHARACTER_COUNT VARCHAR(10) DEFAULT NULL,
  STATUS VARCHAR(5) DEFAULT NULL,
  IN_OUT_BOUND VARCHAR(1) DEFAULT NULL,
  FROM_ROUTING_ID VARCHAR(39) DEFAULT NULL,
  TO_ROUTING_ID VARCHAR(39) DEFAULT NULL,
  INVOICE_IDENTIFIER VARCHAR(30) DEFAULT NULL,
  PRIMARY KEY (SEQNO,SUBSEQNO)  USING BTREE,
  KEY TURNKEY_MESSAGE_LOG_INDEX1 (MESSAGE_DTS),
  KEY TURNKEY_MESSAGE_LOG_INDEX2 (UUID)
) ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_MESSAGE_LOG_DETAIL(
   SEQNO                VARCHAR(8) NOT NULL,
   SUBSEQNO             VARCHAR(5) NOT NULL,
   PROCESS_DTS          VARCHAR(17),
   TASK                 VARCHAR(30),
   STATUS               VARCHAR(5),
   FILENAME             VARCHAR(255),
   UUID                 VARCHAR(40),
   PRIMARY KEY (SEQNO, SUBSEQNO, TASK),
   KEY TURNKEY_MESSAGE_LOG_DETAIL_INDEX1 (FILENAME) USING BTREE
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_SEQUENCE(
   SEQUENCE             VARCHAR(8) NOT NULL,
   PRIMARY KEY (SEQUENCE)
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_SYSEVENT_LOG(
   EVENTDTS             VARCHAR(17) NOT NULL,
   PARTY_ID             VARCHAR(10),
   SEQNO                VARCHAR(8),
   SUBSEQNO             VARCHAR(5),
   ERRORCODE            VARCHAR(4),
   UUID                 VARCHAR(40),
   INFORMATION1         VARCHAR(100),
   INFORMATION2         VARCHAR(100),
   INFORMATION3         VARCHAR(100),
   MESSAGE1             VARCHAR(100),
   MESSAGE2             VARCHAR(100),
   MESSAGE3             VARCHAR(100),
   MESSAGE4             VARCHAR(100),
   MESSAGE5             VARCHAR(100),
   MESSAGE6             VARCHAR(100),
   PRIMARY KEY (EVENTDTS),
   KEY TURNKEY_SYSEVENT_LOG_INDEX1 (SEQNO,SUBSEQNO),
   KEY TURNKEY_SYSEVENT_LOG_INDEX2 (UUID)
)ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_TRANSPORT_CONFIG (
  TRANSPORT_ID VARCHAR(10) NOT NULL,
  TRANSPORT_PASSWORD VARCHAR(60) NOT NULL,
  PRIMARY KEY (TRANSPORT_ID)
) ENGINE=INNODB DEFAULT CHARSET=UTF8;

CREATE TABLE TURNKEY_USER_PROFILE (
  USER_ID VARCHAR(10) NOT NULL,
  USER_PASSWORD VARCHAR(100) DEFAULT NULL,
  USER_ROLE VARCHAR(2) DEFAULT NULL,
  PRIMARY KEY (USER_ID) USING BTREE
) ENGINE=INNODB DEFAULT CHARSET=UTF8;

INSERT INTO TURNKEY_USER_PROFILE (USER_ID,USER_PASSWORD,USER_ROLE) VALUES
 ('ADMIN','{CHTAES}ZO0aLaqsu39koQw6YSTTWSAR2t61','0');

CREATE INDEX TURNKEY_MESSAGE_LOG_UUID_IDX USING BTREE ON TURNKEY_MESSAGE_LOG (UUID,MESSAGE_DTS);