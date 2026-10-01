# Agent API Test Report

**Run:** 2026-08-04 15:18:30  
**Target:** `https://localhost:8000`  
**Model:** `openai/gpt-oss-120b`  
**Results:** 20/20 passed

---

## 1. ✅ List accelerators defined on Db2

**Agent:** `catalog_agent`  
**Question:** List the accelerators that are defined on my Db2  
**HTTP status:** `200`  
**Elapsed:** 12.69s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT ACCELERATORNAME, LOCATION, ACCELERATOR_TYPE FROM SYSACCEL.SYSACCELERATORS ORDER BY ACCELERATORNAME
```

**Answer:**

> The database defines two accelerators:  
>   
> | Accelerator name | Location | Type |  
> |------------------|----------|------|  
> | ACCEL194 | ACCEL194 | 2 |  
> | SIM043   | SIM043   | 2 |  
>   
> These are the only entries found in `SYSACCEL.SYSACCELERATORS`.

---

## 2. ✅ Port and IP for accelerator ACCEL194

**Agent:** `catalog_agent`  
**Question:** List the port number of the accelerator ACCEL194 and its IP address  
**HTTP status:** `200`  
**Elapsed:** 17.78s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT l.PORT, i.IPADDR FROM SYSACCEL.SYSACCELERATORS a JOIN SYSIBM.LOCATIONS l ON a.LOCATION = l.LOCATION JOIN SYSIBM.IPNAMES i ON a.LOCATION = i.LINKNAME WHERE a.ACCELERATORNAME = 'ACCEL194'
```

**Answer:**

> The accelerator **ACCEL194** uses TCP/IP port **1400** and its IP address is **10.101.12.94**.

---

## 3. ✅ IP address of accelerator SIM043

**Agent:** `catalog_agent`  
**Question:** What is the IP address of the accelerator SIM043  
**HTTP status:** `200`  
**Elapsed:** 11.24s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT IPN.IPADDR AS IP_ADDRESS FROM SYSACCEL.SYSACCELERATORS ACC JOIN SYSIBM.IPNAMES IPN ON ACC.LOCATION = IPN.LINKNAME WHERE ACC.ACCELERATORNAME = 'SIM043'
```

**Answer:**

> The accelerator **SIM043** is configured with the IP address **10.101.14.43**.

---

## 4. ✅ Who created accelerator ACCEL194

**Agent:** `catalog_agent`  
**Question:** Who created the accelerator ACCEL194  
**HTTP status:** `200`  
**Elapsed:** 10.89s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT CREATEDBY, CREATEDTS FROM SYSACCEL.SYSACCELERATEDTABLES WHERE ACCELERATORNAME = 'ACCEL194'
```

**Answer:**

> The CREATEDBY column for accelerator ACCEL194 in SYSACCEL.SYSACCELERATEDTABLES shows **KAVYA** as the user who created the accelerator.

---

## 5. ✅ Who created accelerator with IP 10.101.14.43

**Agent:** `catalog_agent`  
**Question:** Who created the accelerator with the IP address 10.101.14.43  
**HTTP status:** `200`  
**Elapsed:** 16.05s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT DISTINCT at.CREATEDBY, at.CREATEDTS
FROM SYSACCEL.SYSACCELERATEDTABLES at
JOIN SYSACCEL.SYSACCELERATORS ac ON at.ACCELERATORNAME = ac.ACCELERATORNAME
JOIN SYSIBM.IPNAMES ip ON ac.LOCATION = ip.LINKNAME
WHERE ip.IPADDR = '10.101.14.43'
ORDER BY at.CREATEDTS DESC FETCH FIRST 10 ROWS ONLY
```

**Answer:**

> The accelerator associated with IP address 10.101.14.43 was created by the user **ZHANTU** (as shown by the CREATEDBY column in the query results).

---

## 6. ✅ All rows of SYSACCELERATORS

**Agent:** `catalog_agent`  
**Question:** Give me all rows of the IDAA catalog table SYSACCELERATORS  
**HTTP status:** `200`  
**Elapsed:** 11.7s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT ACCELERATORNAME, LOCATION, ACCELERATORSRL, ACCELERATOR_TYPE FROM SYSACCEL.SYSACCELERATORS ORDER BY ACCELERATORNAME
```

**Answer:**

> The query returned two accelerator definitions:  
>   
> - **ACCEL194** – located at *ACCEL194*, accelerator type 2, with its internal `ACCELERATORSRL` binary value shown.  
> - **SIM043** – located at *SIM043*, accelerator type 2, with its internal `ACCELERATORSRL` binary value shown.

---

## 7. ✅ All rows of SYSACCELERATEDTABLES

**Agent:** `catalog_agent`  
**Question:** Give me all rows of the IDAA catalog table sysacceleratedtables  
**HTTP status:** `200`  
**Elapsed:** 13.21s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, ACCELERATORNAME, REMOTENAME, REMOTECREATOR, ENABLE, CREATEDBY, CREATEDTS, ALTEREDTS, REFRESH_TIME, SUPPORTLEVEL, ARCHIVE, REMOTELOCATION, FEATURE FROM SYSACCEL.SYSACCELERATEDTABLES ORDER BY NAME
```

**Answer:**

> The query returned **42 rows** from the IDAA catalog table **SYSACCEL.SYSACCELERATEDTABLES**. Each row includes details such as the accelerated table name, its schema owner, the accelerator server name, the remote base table name and creator, enable flag, creator of the accelerator entry, timestamps for creation/alteration, last refresh time, support level, archive status, remote location, and feature flag. The data shows a mix of enabled (`Y`) and disabled (`N`) tables across several accelerators (e.g., ACCEL194, DGREMDB1, SIM043).

---

## 8. ✅ Accelerated tables altered in last month

**Agent:** `catalog_agent`  
**Question:** Has any IDAA accelerated tables been altered in the last month? Give me the alter timestamp, sort by the newest  
**HTTP status:** `200`  
**Elapsed:** 19.85s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, ALTEREDTS FROM SYSACCEL.SYSACCELERATEDTABLES WHERE ALTEREDTS >= (CURRENT TIMESTAMP - 1 MONTH) ORDER BY ALTEREDTS DESC
```

**Answer:**

> No IDAA‑accelerated tables have been altered in the past month; the query returned zero rows.

---

## 9. ✅ Last refresh timestamp of accelerated tables

**Agent:** `catalog_agent`  
**Question:** Give me the last refresh timestamp of the accelerated tables  
**HTTP status:** `200`  
**Elapsed:** 12.03s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, REFRESH_TIME FROM SYSACCEL.SYSACCELERATEDTABLES ORDER BY REFRESH_TIME DESC FETCH FIRST 10 ROWS ONLY
```

**Answer:**

> The most recent refresh among accelerated tables is **2026‑05‑06 05:15:57.121474**, recorded for the table **INCOME_BAND** (schema TPCDS1G_E). The other tables show slightly earlier refresh times, all within the same minute on 2026‑05‑06.

---

## 10. ✅ Accelerated tables with refresh older than 24 hours

**Agent:** `catalog_agent`  
**Question:** Give me the last refresh timestamp of the accelerated tables that are older than 24 hours  
**HTTP status:** `200`  
**Elapsed:** 18.94s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, REFRESH_TIME FROM SYSACCEL.SYSACCELERATEDTABLES WHERE REFRESH_TIME < (CURRENT TIMESTAMP - 24 HOURS) ORDER BY REFRESH_TIME ASC
```

**Answer:**

> The query returned 42 accelerated tables whose `REFRESH_TIME` is older than 24 hours.    
> Among them, the most recent refresh occurred on **2026‑05‑06 05:15:57.121474** (table `INCOME_BAND`).

---

## 11. ✅ All accelerators with connection details

**Agent:** `catalog_agent`  
**Question:** Show me all accelerators and their connection details  
**HTTP status:** `200`  
**Elapsed:** 10.79s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT a.ACCELERATORNAME, a.LOCATION, l.LINKNAME, l.PORT, l.SECURE, l.TRUSTED, i.IPADDR FROM SYSACCEL.SYSACCELERATORS a LEFT JOIN SYSIBM.LOCATIONS l ON a.LOCATION = l.LOCATION LEFT JOIN SYSIBM.IPNAMES i ON l.LINKNAME = i.LINKNAME ORDER BY a.ACCELERATORNAME
```

**Answer:**

> The query returned two accelerators:  
>   
> - **ACCEL194** – location ACCEL194, link ACCEL194, port 1400, not using SSL (SECURE = N), trusted (TRUSTED = Y), IP address 10.101.12.94.    
> - **SIM043** – location SIM043, link SIM043, port 1400, not using SSL (SECURE = N), trusted (TRUSTED = Y), IP address 10.101.14.43.

---

## 12. ✅ Tables accelerated by SIM043

**Agent:** `catalog_agent`  
**Question:** List all tables that are accelerated by SIM043  
**HTTP status:** `200`  
**Elapsed:** 12.02s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR FROM SYSACCEL.SYSACCELERATEDTABLES WHERE ACCELERATORNAME = 'SIM043' ORDER BY NAME
```

**Answer:**

> The accelerator **SIM043** is configured for nine tables:  
>   
> | Table (NAME) | Schema (CREATOR) |  
> |--------------|-----------------|  
> | CUSTOMER     | TPCH            |  
> | LINEITEM     | TPCH            |  
> | NATION       | TPCH            |  
> | ORDERS       | TPCH            |  
> | PART         | TPCH            |  
> | PART (TPCH30M_A) | TPCH30M_A |  
> | PARTSUPP     | TPCH            |  
> | REGION       | TPCH            |  
> | SUPPLIER     | TPCH            |  
>   
> These are the tables currently accelerated by SIM043.

---

## 13. ✅ Find currently active accelerators

**Agent:** `catalog_agent`  
**Question:** Find accelerators that are currently active  
**HTTP status:** `200`  
**Elapsed:** 13.16s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, ACCELERATORNAME, ENABLE, CREATEDTS FROM SYSACCEL.SYSACCELERATEDTABLES WHERE ENABLE = 'Y' ORDER BY CREATEDTS DESC FETCH FIRST 10 ROWS ONLY
```

**Answer:**

> The query returned the ten most recently created accelerated tables that are currently active (ENABLE = ‘Y’). All entries use the same accelerator server **ACCEL194** and were created on 2026‑05‑06, with tables such as **TIME_DIM**, **STORE_SALES**, **STORE**, **PROMOTION**, **ITEM**, etc.

---

## 14. ✅ Authorization mappings for accelerator ACCEL194

**Agent:** `catalog_agent`  
**Question:** Show me the authorization mappings for accelerator ACCEL194  
**HTTP status:** `200`  
**Elapsed:** 34.3s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, CREATEDBY, ENABLE FROM SYSACCEL.SYSACCELERATEDTABLES WHERE ACCELERATORNAME = 'ACCEL194'
```

**Answer:**

> The query on **SYSACCEL.SYSACCELERATEDTABLES** for accelerator **ACCEL194** returned 22 rows.    
>   
> - **22 accelerated tables** are defined for this accelerator.    
> - Tables in the **SUPER** schema (e.g., ALIGNMENT, ATTRIBUTE, COLOUR, GENDER, HERO_ATTRIBUTE, HERO_POWER, PUBLISHER, RACE, SUPERHERO, SUPERPOWER) are **disabled** (`ENABLE = 'N'`).    
> - Tables in the **TPCDS1G_E** schema (e.g., CUSTOMER, CUSTOMER_ADDRESS, CUSTOMER_DEMOGRAPHICS, DATE_DIM, HOUSEHOLD_DEMOGRAPHICS, HROYSYNC, INCOME_BAND, ITEM, PROMOTION, STORE, STORE_SALES, TIME_DIM) are **enabled** (`ENABLE = 'Y'`).    
> - All entries were **created by the authorization ID “KAVYA”**.    
>   
> Thus, ACCEL194 has a mix of enabled and disabled accelerated tables, with the creator ID “KAVYA” for every mapping.

---

## 15. ✅ All remote locations defined for IDAA

**Agent:** `catalog_agent`  
**Question:** List all remote locations defined for IDAA  
**HTTP status:** `200`  
**Elapsed:** 10.98s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT LOCATION, LINKNAME, PORT, DBALIAS, TRUSTED, SECURE FROM SYSIBM.LOCATIONS ORDER BY LOCATION
```

**Answer:**

> The IDAA remote locations defined in the catalog are:  
>   
> - **ACCEL194** – link name ACCEL194, port 1400, trusted (Y), not secure (N)    
> - **DGREMDB1** – link name DGREMDB1, port 15001, trusted (Y), not secure (N)    
> - **DGREMDB4** – link name DGREMDB4, port 15004, trusted (Y), not secure (N)    
> - **SIM043** – link name SIM043, port 1400, trusted (Y), not secure (N)

---

## 16. ✅ All TCP/IP connections for accelerators

**Agent:** `catalog_agent`  
**Question:** Show me all TCP/IP connections for accelerators  
**HTTP status:** `200`  
**Elapsed:** 16.65s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT A.ACCELERATORNAME, A.LOCATION, L.PORT, I.IPADDR FROM SYSACCEL.SYSACCELERATORS A JOIN SYSIBM.LOCATIONS L ON A.LOCATION = L.LOCATION JOIN SYSIBM.IPNAMES I ON L.LINKNAME = I.LINKNAME ORDER BY A.ACCELERATORNAME
```

**Answer:**

> The query returned two accelerator entries, each showing its name, associated location, the TCP/IP port (1400), and the IP address of the remote host:  
>   
> - **ACCEL194** – location **ACCEL194**, port **1400**, IP **10.101.12.94**    
> - **SIM043** – location **SIM043**, port **1400**, IP **10.101.14.43**

---

## 17. ✅ Accelerated tables not refreshed in last week

**Agent:** `catalog_agent`  
**Question:** Find accelerated tables that haven't been refreshed in the last week  
**HTTP status:** `200`  
**Elapsed:** 34.07s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, REFRESH_TIME FROM SYSACCEL.SYSACCELERATEDTABLES WHERE REFRESH_TIME < CURRENT TIMESTAMP - 7 DAYS ORDER BY REFRESH_TIME ASC
```

**Answer:**

> The query returned **42 accelerated tables** whose `REFRESH_TIME` is older than one week (including the default timestamp of `0001‑01‑01 00:00:00`, which indicates they have never been refreshed).    
>   
> Key points:  
>   
> - All tables listed under schemas such as `SUPER`, `TOXIC`, `SYSACCEL`, and many test schemas have a refresh timestamp of `0001‑01‑01`, meaning they have never been refreshed.  
> - Only a few tables (e.g., `LINEITEM`, `ORDERS`, `PART`, `PARTSUPP`, `CUSTOMER`, `SUPPLIER`, `NATION`, `REGION`, and several TPC‑DS tables) show recent refresh timestamps (e.g., `2026‑01‑23` or `2026‑05‑05`), indicating they were refreshed within the last week.    
>   
> Thus, the majority of accelerated tables in the catalog have not been refreshed in the past week.

---

## 18. ✅ Count of accelerated tables per accelerator

**Agent:** `catalog_agent`  
**Question:** Get the count of accelerated tables per accelerator  
**HTTP status:** `200`  
**Elapsed:** 10.91s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT ACCELERATORNAME, COUNT(*) AS TABLE_COUNT FROM SYSACCEL.SYSACCELERATEDTABLES GROUP BY ACCELERATORNAME ORDER BY TABLE_COUNT DESC
```

**Answer:**

> The query returned the number of accelerated tables for each accelerator, ordered by the highest count:  
>   
> - **ACCEL194** – 22 tables    
> - **DGREMDB1** – 9 tables    
> - **SIM043** – 9 tables    
> - **DGREMDB4** – 2 tables

---

## 19. ✅ Accelerators with IP addresses sorted by IP

**Agent:** `catalog_agent`  
**Question:** Show me accelerators with their IP addresses sorted by IP  
**HTTP status:** `200`  
**Elapsed:** 13.65s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT A.ACCELERATORNAME, I.IPADDR FROM SYSACCEL.SYSACCELERATORS A JOIN SYSIBM.LOCATIONS L ON A.LOCATION = L.LOCATION JOIN SYSIBM.IPNAMES I ON L.LINKNAME = I.LINKNAME ORDER BY I.IPADDR
```

**Answer:**

> The query returned two accelerator entries, listed with their IP addresses in ascending order:  
>   
> - **ACCEL194** – IP `10.101.12.94`    
> - **SIM043** – IP `10.101.14.43`

---

## 20. ✅ Accelerated tables altered today

**Agent:** `catalog_agent`  
**Question:** List accelerated tables that were altered today  
**HTTP status:** `200`  
**Elapsed:** 13.94s  
**Graph turns:** 1  

**Last SQL Query:**
```sql
SELECT NAME, CREATOR, ALTEREDTS, CREATEDBY FROM SYSACCEL.SYSACCELERATEDTABLES WHERE DATE(ALTEREDTS) = CURRENT DATE ORDER BY ALTEREDTS DESC
```

**Answer:**

> The query returned no rows, indicating that no accelerated tables were altered on the current date.

---

*Total: 20 | Passed: 20 | Failed: 0 | Model: openai/gpt-oss-120b*