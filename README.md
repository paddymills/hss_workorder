
# Work Order 2.0

## Components

- Init from BOM
- Code move/release
- ChargeRef assign
- Change management
- CDS (gui/webapp)
- SAP confirmations

## Service/Endpoint

- core
    - db/SimTrans communication
    - data processing
    - asset management
- workorder init
    - read engineering BOM/db
    - operations inference
        - Drill/Punch
        - End-Mill/NX
        - Press
        - Rojar
- CDS
    - save data
    - sync clients
    - eReport delivery
- ChargeRef assigment
    - update db
    - generate eReports
- code release/pull
    - cp/del CIMNET
    - checked NC
- change management
    - assess what needs done
    - update/create work orders
- SAP confirmations
    - SimTrans?
    - Interval: after each program

## CDS db table

| Program | Checked | Printed | Notes | Released |
| --- | --- | --- | --- | --- |
| 45925 | PM | 6/28/2021 | | 6/24/2021 |
| 46025 | | | | |
| 46049 | -- | 6/23/2021 | x1a, x1b | 6/22/2021 |
