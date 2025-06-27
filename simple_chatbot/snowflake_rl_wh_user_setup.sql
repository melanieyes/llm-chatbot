
-- It is not recommended to use this in production.
-- Please use your own keypair and setup.
-- START WITH CREATING YOUR OWN KEYPAIR IF YOU HAVE NOT DONE SO: https://docs.snowflake.com/en/user-guide/key-pair-auth
----------------------------------------------------------------------------------------------------------------

use role useradmin;

create user if not exists SVC_LITELLM_DEMO;
alter user SVC_LITELLM_DEMO set TYPE = SERVICE;
alter user SVC_LITELLM_DEMO set RSA_PUBLIC_KEY = 'your_public_key_here';


USE ROLE SECURITYADMIN;
CREATE ROLE IF NOT EXISTS RL_LITELLM_DEMO;
-- Grant all custom roles to SYSADMIN - Snowflake best practices
GRANT ROLE RL_LITELLM_DEMO TO ROLE SYSADMIN;
GRANT ROLE RL_LITELLM_DEMO TO USER SVC_LITELLM_DEMO;

USE ROLE SYSADMIN;
CREATE WAREHOUSE IF NOT EXISTS WH_LITELLM_DEMO
WAREHOUSE_SIZE = XSMALL
WAREHOUSE_TYPE = 'STANDARD'
AUTO_SUSPEND = 60
AUTO_RESUME = True
;

USE ROLE SECURITYADMIN;
-- Granting SYSADMIN and SECURITYADMIN the ability to modify the warehosue
GRANT OPERATE,USAGE,MONITOR,MODIFY ON WAREHOUSE WH_LITELLM_DEMO TO ROLE SYSADMIN;
GRANT OPERATE,USAGE,MONITOR,MODIFY ON WAREHOUSE WH_LITELLM_DEMO TO ROLE SECURITYADMIN;
CREATE ROLE IF NOT EXISTS RL_WH_LITELLM_DEMO;
GRANT OPERATE, USAGE ON WAREHOUSE WH_LITELLM_DEMO TO ROLE RL_WH_LITELLM_DEMO;
--following snowflake best practice and granting all custom roles to sysadmin
GRANT ROLE RL_WH_LITELLM_DEMO TO ROLE SYSADMIN;

-- CREATE OVERALL LAB ROLE
USE ROLE SECURITYADMIN;
GRANT ROLE RL_WH_LITELLM_DEMO TO ROLE RL_LITELLM_DEMO;


-- use 

USE ROLE SECURITYADMIN;
GRANT ROLE RL_LITELLM_DEMO to user SVC_LITELLM_DEMO;
GRANT ROLE RL_LITELLM_DEMO to user SVC_LITELLM_DEMO__TEST;

-- Enable Cortex in US region in case your current region is not US
use role accountadmin;
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_US';

-- test access to sample database
use role RL_LITELLM_DEMO
select * from SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.CUSTOMER;
