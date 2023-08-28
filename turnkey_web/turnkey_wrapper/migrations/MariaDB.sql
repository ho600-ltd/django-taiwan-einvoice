CREATE TABLE FROM_CONFIG
(
    TRANSPORT_ID CHARACTER VARYING(10),
    TRANSPORT_PASSWORD CHARACTER VARYING(45),
    PARTY_ID CHARACTER VARYING(10) NOT NULL,
    PARTY_DESCRIPTION CHARACTER VARYING(200),
    ROUTING_ID CHARACTER VARYING(39),
    ROUTING_DESCRIPTION CHARACTER VARYING(200),
    SIGN_ID CHARACTER VARYING(4),
    SUBSTITUTE_PARTY_ID CHARACTER VARYING(10),
    CONSTRAINT FROM_CONFIG_PK1 PRIMARY KEY (PARTY_ID)
);

CREATE INDEX FROM_CONFIG_INDEX1 ON FROM_CONFIG(SUBSTITUTE_PARTY_ID);

CREATE TABLE SCHEDULE_CONFIG
(
    TASK CHARACTER VARYING(30) NOT NULL,
    ENABLE CHARACTER VARYING(1),
    SCHEDULE_TYPE CHARACTER VARYING(10),
    SCHEDULE_WEEK CHARACTER VARYING(15),
    SCHEDULE_TIME CHARACTER VARYING(50),
    SCHEDULE_PERIOD CHARACTER VARYING(10),
    SCHEDULE_RANGE CHARACTER VARYING(15),
    CONSTRAINT SCHEDULE_CONFIG_PK1 PRIMARY KEY (TASK)
);


CREATE TABLE SIGN_CONFIG
(
    SIGN_ID CHARACTER VARYING(4) NOT NULL,
    SIGN_TYPE CHARACTER VARYING(10) DEFAULT NULL,
    PFX_PATH CHARACTER VARYING(100) DEFAULT NULL,
    SIGN_PASSWORD CHARACTER VARYING(60) NOT NULL,
    CONSTRAINT SIGN_CONFIG_PK1 PRIMARY KEY (SIGN_ID)
);

CREATE TABLE TASK_CONFIG
(
    CATEGORY_TYPE CHARACTER VARYING(5) NOT NULL,
    PROCESS_TYPE CHARACTER VARYING(10) NOT NULL,
    TASK CHARACTER VARYING(15) NOT NULL,
    SRC_PATH CHARACTER VARYING(200),
    TARGET_PATH CHARACTER VARYING(200),
    FILE_FORMAT CHARACTER VARYING(20),
    VERSION CHARACTER VARYING(5),
    ENCODING CHARACTER VARYING(15),
    TRANS_CHINESE_DATE CHARACTER VARYING(1),
    CONSTRAINT TASK_CONFIG_PK1 PRIMARY KEY (CATEGORY_TYPE, PROCESS_TYPE, TASK)
);

CREATE TABLE TO_CONFIG
(
    PARTY_ID CHARACTER VARYING(10) NOT NULL,
    PARTY_DESCRIPTION CHARACTER VARYING(200),
    ROUTING_ID CHARACTER VARYING(39),
    ROUTING_DESCRIPTION CHARACTER VARYING(200),
    FROM_PARTY_ID CHARACTER VARYING(10) NOT NULL,
    CONSTRAINT TO_CONFIG_PK1 PRIMARY KEY (FROM_PARTY_ID, PARTY_ID)
);

CREATE TABLE TURNKEY_MESSAGE_LOG
(
    SEQNO CHARACTER VARYING(8) NOT NULL,
    SUBSEQNO CHARACTER VARYING(5) NOT NULL,
    UUID CHARACTER VARYING(40) DEFAULT NULL,
    MESSAGE_TYPE CHARACTER VARYING(10) DEFAULT NULL,
    CATEGORY_TYPE CHARACTER VARYING(5) DEFAULT NULL,
    PROCESS_TYPE CHARACTER VARYING(10) DEFAULT NULL,
    FROM_PARTY_ID CHARACTER VARYING(10) DEFAULT NULL,
    TO_PARTY_ID CHARACTER VARYING(10) DEFAULT NULL,
    MESSAGE_DTS CHARACTER VARYING(17) DEFAULT NULL,
    CHARACTER_COUNT CHARACTER VARYING(10) DEFAULT NULL,
    STATUS CHARACTER VARYING(5) DEFAULT NULL,
    IN_OUT_BOUND CHARACTER VARYING(1) DEFAULT NULL,
    FROM_ROUTING_ID CHARACTER VARYING(39) DEFAULT NULL,
    TO_ROUTING_ID CHARACTER VARYING(39) DEFAULT NULL,
    INVOICE_IDENTIFIER CHARACTER VARYING(30) DEFAULT NULL,
    CONSTRAINT TURNKEY_MESSAGE_LOG_PK1 PRIMARY KEY (SEQNO, SUBSEQNO)
);

CREATE INDEX TURNKEY_MESSAGE_LOG_INDEX1 ON TURNKEY_MESSAGE_LOG(MESSAGE_DTS);


CREATE INDEX TURNKEY_MESSAGE_LOG_INDEX2 ON TURNKEY_MESSAGE_LOG(UUID);

CREATE INDEX TURNKEY_MESSAGE_LOG_UUID_IDX USING BTREE ON TURNKEY_MESSAGE_LOG (UUID,MESSAGE_DTS);

CREATE TABLE TURNKEY_MESSAGE_LOG_DETAIL
(
    SEQNO CHARACTER VARYING(8) NOT NULL,
    SUBSEQNO CHARACTER VARYING(5) NOT NULL,
    PROCESS_DTS CHARACTER VARYING(17),
    TASK CHARACTER VARYING(30) NOT NULL,
    STATUS CHARACTER VARYING(5),
    FILENAME CHARACTER VARYING(300),
    UUID CHARACTER VARYING(40),
    CONSTRAINT TURNKEY_MESSAGE_LOG_DETAIL_PK1 PRIMARY KEY (SEQNO, SUBSEQNO, TASK)
);

CREATE INDEX TURNKEY_MESSAGE_LOG_DETAIL_INDEX1 ON TURNKEY_MESSAGE_LOG_DETAIL(FILENAME);

CREATE TABLE TURNKEY_SEQUENCE
(
    SEQUENCE CHARACTER VARYING(8) NOT NULL,
    CONSTRAINT TURNKEY_SEQUENCE_PK1 PRIMARY KEY (SEQUENCE)
);


CREATE TABLE TURNKEY_SYSEVENT_LOG
(
    EVENTDTS CHARACTER VARYING(17) NOT NULL,
    PARTY_ID CHARACTER VARYING(10),
    SEQNO CHARACTER VARYING(8),
    SUBSEQNO CHARACTER VARYING(5),
    ERRORCODE CHARACTER VARYING(4),
    UUID CHARACTER VARYING(40),
    INFORMATION1 CHARACTER VARYING(100),
    INFORMATION2 CHARACTER VARYING(100),
    INFORMATION3 CHARACTER VARYING(100),
    MESSAGE1 CHARACTER VARYING(100),
    MESSAGE2 CHARACTER VARYING(100),
    MESSAGE3 CHARACTER VARYING(100),
    MESSAGE4 CHARACTER VARYING(100),
    MESSAGE5 CHARACTER VARYING(100),
    MESSAGE6 CHARACTER VARYING(100),
    CONSTRAINT TURNKEY_SYSEVENT_LOG_PK1 PRIMARY KEY (EVENTDTS)
);

CREATE INDEX TURNKEY_SYSEVENT_LOG_INDEX1 ON TURNKEY_SYSEVENT_LOG(SEQNO, SUBSEQNO);


CREATE INDEX TURNKEY_SYSEVENT_LOG_INDEX2 ON TURNKEY_SYSEVENT_LOG(UUID);

CREATE TABLE TURNKEY_TRANSPORT_CONFIG
(
    TRANSPORT_ID CHARACTER VARYING(10) NOT NULL,
    TRANSPORT_PASSWORD CHARACTER VARYING(60) NOT NULL,
    CONSTRAINT TURNKEY_TRANSPORT_CONFIG_PK1 PRIMARY KEY (TRANSPORT_ID)
);

CREATE TABLE TURNKEY_USER_PROFILE
(
    USER_ID CHARACTER VARYING(10) NOT NULL,
    USER_PASSWORD CHARACTER VARYING(100) NOT NULL,
    USER_ROLE CHARACTER VARYING(2) ,
    CONSTRAINT TURNKEY_USER_PROFILE_PK1 PRIMARY KEY (USER_ID)
);


INSERT INTO TURNKEY_USER_PROFILE (USER_ID,USER_PASSWORD,USER_ROLE) VALUES
 ('ADMIN','{CHTAES}ZO0aLaqsu39koQw6YSTTWSAR2t61','0');