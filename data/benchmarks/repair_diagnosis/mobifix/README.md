# Open Repair Alliance (ORA) - MobiFix Smartphone Diagnostic Benchmark

## Overview
The MobiFix dataset is derived from community-collected repair events (Restart Parties, Repair Cafés) under the Open Repair Data Standard (ORDS). It contains approximately 1,900 categorized smartphone repair attempts.

## Schema
* `id` (string): Unique event/repair record ID.
* `product_category` (string): Standardized category (`Mobile`).
* `partner_product_category` (string): Partner raw category string (e.g., `Smartphone`, `Cell`).
* `brand` (string): Manufacturer (e.g., `Apple`, `Samsung`, `Xiaomi`, `Google`).
* `year_of_manufacture` (integer / YYYY): Release/manufacture year, if documented.
* `product_age` (float): Age of device in years at the time of repair.
* `problem` (string): Customer/user reported description of the defect or symptom.
* `repair_status` (string): Outcome of the attempt (`Fixed`, `Repairable`, `End of life`).
* `repair_barrier_if_end_of_life` (string): Reason device was not fixed (e.g., `No spare parts`, `Parts too expensive`, `Glued design`).

## Category Mapping to REVIVAI
REVIVAI's `FaultDiagnosisAgent` classifies problems into 7 canonical categories. MobiFix problem descriptions map as follows:
1. `cracked_screen`: Display, touch digitizer, glass cracks, black screen, vertical lines.
2. `battery`: Fast drain, premature shutdown, won't hold charge, bulging/swelling.
3. `charging`: Port loose, cable falls out, won't recognize charger, slow charging.
4. `liquid_damage`: Dropped in water, moisture warning, corrosion.
5. `overheating`: Hot to touch during normal usage or charging.
6. `performance`: Slow, freezing, app crashes, storage full, bootloop.
7. `unclear`: Ambiguous or fragmented description requiring follow-up clarification.

## License & Provenance
* **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
* **Attribution:** Open Repair Alliance (openrepair.org).
* **Caveat:** Problem labels represent user/volunteer triage notes, not professional cleanroom teardown diagnoses.
