"""Generate sample PDF documents for smoke testing the RAG pipeline.

Run: uv run python scripts/generate_sample_docs.py
Output: six PDFs under data/raw/
"""

from pathlib import Path

from fpdf import FPDF

OUT_DIR = Path("data/raw")


def _clean(text: str) -> str:
    """Replace non-latin-1 characters with ASCII equivalents."""
    return (
        text.replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def make_pdf(filename: str, title: str, sections: list[tuple[str, str]]) -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, _clean(title), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, _clean(heading), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, _clean(body))
        pdf.ln(4)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / filename
    pdf.output(str(path))
    print(f"Created {path}")
    return path


def generate_all() -> list[Path]:
    paths: list[Path] = []

    paths.append(
        make_pdf(
            "odoo_inventory_guide.pdf",
            "Odoo 17 Inventory Module — User Guide",
            [
                (
                    "1. Overview",
                    (
                        "The Odoo Inventory module manages the full supply-chain lifecycle: receipts, "
                        "internal transfers, delivery orders, and real-time stock valuation. It integrates "
                        "with Purchase, Sales, and Manufacturing to keep stock levels accurate across all "
                        "warehouse locations."
                    ),
                ),
                (
                    "2. Warehouse Configuration",
                    (
                        "Navigate to Inventory > Configuration > Warehouses to create or edit a warehouse. "
                        "Each warehouse has a short code (e.g. WH) used as a prefix for all its operation "
                        "types. You can enable multi-step routes (2-step or 3-step) for both incoming and "
                        "outgoing shipments under the Shipments tab."
                    ),
                ),
                (
                    "3. Receipts (Incoming Shipments)",
                    (
                        "When a Purchase Order is confirmed, Odoo automatically creates a Receipt in "
                        "state 'Ready'. To validate: open the receipt, check quantities against the "
                        "delivery note, then click Validate. If actual quantity differs from demand, "
                        "Odoo prompts to create a backorder for the remaining quantity. "
                        "Serial numbers or lot numbers can be assigned during validation if tracking is enabled."
                    ),
                ),
                (
                    "4. Delivery Orders (Outgoing Shipments)",
                    (
                        "Delivery orders are generated automatically when a Sales Order is confirmed. "
                        "The default operation type is 'Delivery Orders' (OUT). "
                        "To process: open the delivery, click Check Availability to reserve stock, "
                        "then click Validate to confirm the shipment. "
                        "If stock is insufficient, use the Unreserve button and replenish first."
                    ),
                ),
                (
                    "5. Internal Transfers",
                    (
                        "Internal transfers move stock between locations within the same warehouse or "
                        "between warehouses. Create one via Inventory > Operations > Transfers > New. "
                        "Set Operation Type to 'Internal Transfer', choose source and destination locations, "
                        "add product lines, then validate. "
                        "This is commonly used to move goods from a receiving area (WH/Input) to storage (WH/Stock)."
                    ),
                ),
                (
                    "6. Inventory Adjustments",
                    (
                        "Use Inventory > Operations > Physical Inventory to perform a stock count. "
                        "Odoo shows the system quantity next to an editable 'Counted Quantity' field. "
                        "Enter actual counted quantities, then click Apply All to post adjustments. "
                        "Each adjustment creates a journal entry in the accounting module if perpetual "
                        "inventory valuation is enabled."
                    ),
                ),
                (
                    "7. Reordering Rules",
                    (
                        "Reordering rules automate replenishment. Navigate to Inventory > Configuration > "
                        "Reordering Rules. Set a product, location, minimum quantity (Min Qty), and maximum "
                        "quantity (Max Qty). When stock falls below Min Qty, the scheduler creates a "
                        "Purchase Order or Manufacturing Order automatically. "
                        "Run the scheduler manually via Inventory > Operations > Replenishment."
                    ),
                ),
                (
                    "8. Lot and Serial Number Tracking",
                    (
                        "Enable tracking per product under the product form > Inventory tab > Tracking. "
                        "Options: By Unique Serial Number (one unit per serial), By Lots (batch of units). "
                        "During receipts and deliveries, Odoo requires assigning a lot/serial number. "
                        "Full traceability is available via the Traceability report on any stock move."
                    ),
                ),
                (
                    "9. Stock Valuation",
                    (
                        "Odoo supports two costing methods: Average Cost (AVCO) and First In First Out (FIFO). "
                        "Set the costing method per product category under Inventory > Configuration > "
                        "Product Categories. FIFO is recommended for perishable goods. "
                        "Stock valuation reports are available under Inventory > Reporting > Inventory Valuation."
                    ),
                ),
                (
                    "10. Key Reports",
                    (
                        "- Stock report: current on-hand quantities per location.\n"
                        "- Inventory valuation: total stock value by product.\n"
                        "- Forecasted inventory: projected stock over time based on confirmed orders.\n"
                        "- Traceability: full movement history for a lot or serial number.\n"
                        "All reports are accessible under Inventory > Reporting."
                    ),
                ),
            ],
        )
    )

    paths.append(
        make_pdf(
            "warehouse_sop.pdf",
            "Warehouse Standard Operating Procedure (SOP)",
            [
                (
                    "Purpose and Scope",
                    (
                        "This SOP defines the standard procedures for all warehouse operations including "
                        "receiving, put-away, picking, packing, and shipping. It applies to all warehouse "
                        "staff, supervisors, and logistics coordinators. The goal is to ensure inventory "
                        "accuracy, operational efficiency, and compliance with safety regulations."
                    ),
                ),
                (
                    "Roles and Responsibilities",
                    (
                        "Warehouse Manager: oversees all operations, approves adjustments above 50 units, "
                        "reviews daily KPI report.\n"
                        "Receiving Clerk: inspects incoming goods, creates GRN in the WMS, labels items.\n"
                        "Inventory Controller: conducts cycle counts, investigates discrepancies, updates records.\n"
                        "Picker/Packer: fulfills pick lists, packs orders per standard, hands to shipping.\n"
                        "Shipping Clerk: generates shipping labels, coordinates with carriers, records dispatches."
                    ),
                ),
                (
                    "Receiving Procedure",
                    (
                        "Step 1: Verify the delivery truck against the scheduled appointment list.\n"
                        "Step 2: Inspect packaging for visible damage before unloading.\n"
                        "Step 3: Count items against the Purchase Order (PO) and supplier delivery note.\n"
                        "Step 4: For discrepancies > 2%, hold the shipment and notify the Warehouse Manager.\n"
                        "Step 5: Create a Goods Receipt Note (GRN) in the WMS within 30 minutes of completion.\n"
                        "Step 6: Apply location labels and move items to the staging area."
                    ),
                ),
                (
                    "Put-Away Procedure",
                    (
                        "Step 1: Retrieve the put-away task from the WMS after GRN creation.\n"
                        "Step 2: Scan the item barcode to confirm identity.\n"
                        "Step 3: Follow the WMS-suggested bin location. Override only with supervisor approval.\n"
                        "Step 4: Scan the bin barcode to confirm storage.\n"
                        "Step 5: For heavy items (> 25 kg), use a pallet jack. For fragile items, place on "
                        "designated shelves with 'FRAGILE' label.\n"
                        "Step 6: Confirm put-away in the WMS to update stock levels in real time."
                    ),
                ),
                (
                    "Cycle Count Procedure",
                    (
                        "Cycle counts are performed on a rolling schedule: A-class SKUs weekly, "
                        "B-class monthly, C-class quarterly.\n"
                        "Step 1: Print the count sheet from the WMS for the assigned zone.\n"
                        "Step 2: Count without looking at system quantities (blind count).\n"
                        "Step 3: Enter counted quantities into the WMS.\n"
                        "Step 4: Investigate variances > 1 unit before approving the adjustment.\n"
                        "Step 5: Inventory Controller approves adjustments; Warehouse Manager approves "
                        "variances with value > 500 USD."
                    ),
                ),
                (
                    "Picking Procedure",
                    (
                        "Step 1: Accept a pick task in the WMS (FIFO or wave picking).\n"
                        "Step 2: Navigate to the source location shown on the screen or RF gun.\n"
                        "Step 3: Scan product barcode. If mismatch, do NOT pick — report to supervisor.\n"
                        "Step 4: Pick the exact quantity shown. Short-pick only with supervisor approval.\n"
                        "Step 5: Place items in the labeled tote or pallet.\n"
                        "Step 6: Confirm pick in WMS to move stock to the packing area."
                    ),
                ),
                (
                    "Packing and Shipping",
                    (
                        "Step 1: Verify picked items against the Sales Order packing list.\n"
                        "Step 2: Select appropriate packaging based on item size and fragility.\n"
                        "Step 3: Apply bubble wrap or dunnage for fragile items.\n"
                        "Step 4: Print and attach shipping label. Confirm label matches the order.\n"
                        "Step 5: Hand parcel to the shipping clerk with a signed handover sheet.\n"
                        "Step 6: Shipping clerk scans and manifests parcels with the carrier system "
                        "before end of shift."
                    ),
                ),
                (
                    "Safety Rules",
                    (
                        "- Always wear steel-toed boots and a high-visibility vest in the warehouse.\n"
                        "- Maximum forklift speed is 8 km/h in aisles, 4 km/h near pedestrian zones.\n"
                        "- Never stack pallets higher than 3 meters without supervisor approval.\n"
                        "- Report any injury, near-miss, or equipment damage within 1 hour to the manager.\n"
                        "- Fire exits must remain clear at all times. Blocking a fire exit results in "
                        "immediate disciplinary action."
                    ),
                ),
                (
                    "KPIs and Reporting",
                    (
                        "The Warehouse Manager reviews the following KPIs daily:\n"
                        "- Receiving accuracy: GRN lines with zero discrepancy / total GRN lines (target > 98%).\n"
                        "- Inventory accuracy: items counted correctly / total items counted (target > 99.5%).\n"
                        "- Order fulfillment rate: orders shipped on time / total orders (target > 97%).\n"
                        "- Pick error rate: incorrect picks / total picks (target < 0.5%).\n"
                        "Reports are generated from the WMS at 08:00 daily and emailed to the operations team."
                    ),
                ),
            ],
        )
    )

    paths.append(
        make_pdf(
            "purchase_sop.pdf",
            "Purchase-to-Pay Standard Operating Procedure",
            [
                (
                    "Purpose",
                    (
                        "This SOP covers requisition, purchase order creation, three-way matching, "
                        "and supplier payment release. It applies to Procurement, Accounts Payable, "
                        "and department requesters."
                    ),
                ),
                (
                    "Approval Limits",
                    (
                        "Purchase requisitions are approved by role, not by the requester themselves. "
                        "Limits: team lead up to 2,000 USD; department head up to 10,000 USD; "
                        "CFO above 10,000 USD. Splitting one need into multiple POs to avoid a "
                        "threshold is prohibited and is treated as a control breach."
                    ),
                ),
                (
                    "Three-Way Match",
                    (
                        "Accounts Payable must complete a three-way match before releasing payment: "
                        "the Purchase Order, the Goods Receipt Note, and the supplier invoice. "
                        "A variance above 1% or 50 USD (whichever is greater) is parked and sent "
                        "back to Procurement. Payment is never released on invoice-only evidence."
                    ),
                ),
                (
                    "Preferred Suppliers",
                    (
                        "New suppliers require a vendor onboarding form, tax ID check, and a "
                        "signed code of conduct. Spot buys from unlisted suppliers above 500 USD "
                        "need Procurement Manager approval. Catalog items must be ordered from "
                        "the preferred-supplier list in the purchasing module."
                    ),
                ),
            ],
        )
    )

    paths.append(
        make_pdf(
            "quality_control_sop.pdf",
            "Incoming Quality Control SOP",
            [
                (
                    "Scope",
                    (
                        "Incoming Quality Control (IQC) inspects purchased goods before they are "
                        "released to WH/Stock. IQC does not replace the receiving count; it is a "
                        "separate quality gate after GRN creation."
                    ),
                ),
                (
                    "Sampling Plan",
                    (
                        "Use a skip-lot plan for certified suppliers with six consecutive accepted "
                        "lots. For all other suppliers, inspect 10% of units in the lot, with a "
                        "minimum of 8 units and a maximum of 50 units per SKU per receipt. "
                        "Critical safety parts (class S) are 100% inspected, no skip-lot."
                    ),
                ),
                (
                    "Hold and Release",
                    (
                        "Failed lots are moved to location WH/QualityHold. The Quality Engineer "
                        "issues an NCR within 4 business hours. Warehouse staff must not pick "
                        "from QualityHold. Only a Quality Engineer can release stock to WH/Stock "
                        "after rework or supplier replacement."
                    ),
                ),
                (
                    "Records",
                    (
                        "Keep IQC records for 36 months. Each record includes lot number, sample "
                        "size, measured defects, disposition (accept, reject, concession), and "
                        "the inspector badge ID."
                    ),
                ),
            ],
        )
    )

    paths.append(
        make_pdf(
            "returns_rma_sop.pdf",
            "Customer Returns and RMA Procedure",
            [
                (
                    "When an RMA is required",
                    (
                        "Customer returns need a Return Merchandise Authorization (RMA) number "
                        "before the warehouse may accept the parcel. Walk-in returns without an "
                        "RMA are refused at the dock. Sales creates the RMA in the helpdesk; "
                        "Warehouse only receives against that RMA."
                    ),
                ),
                (
                    "Inspection on return",
                    (
                        "Restock to available inventory only if the item is unopened, in original "
                        "packaging, and within 14 days of delivery. Opened but unused items go to "
                        "WH/ReturnsQuarantine for Quality review. Damaged items are scrapped with "
                        "a photo attached to the RMA. Refunds are blocked until Warehouse posts "
                        "the return receipt."
                    ),
                ),
                (
                    "Credit and replacement",
                    (
                        "Replacement ships only after the return receipt is validated. Credit notes "
                        "are issued by Finance within 3 business days of validation. Do not issue "
                        "a replacement and a full refund for the same RMA line."
                    ),
                ),
            ],
        )
    )

    paths.append(
        make_pdf(
            "odoo_sales_guide.pdf",
            "Odoo 17 Sales Module — User Guide",
            [
                (
                    "Quotations",
                    (
                        "Create a quotation from Sales > Orders > Quotations > New. Set the "
                        "customer, add order lines, then send by email. Default quotation validity "
                        "is 15 days from the quotation date. After expiry, the Confirm button is "
                        "blocked until a salesperson clicks Extend Validity."
                    ),
                ),
                (
                    "Confirmation and reservation",
                    (
                        "Confirming a quotation creates a Sales Order and, if the Inventory app is "
                        "installed, a delivery order. Stock is reserved according to the warehouse "
                        "outgoing route. Partial confirmation of selected lines is not supported; "
                        "use optional products or a new quotation instead."
                    ),
                ),
                (
                    "Discounts and pricelists",
                    (
                        "Line discounts above 15% require Sales Manager approval via the chatter "
                        "approval activity. Pricelists are assigned on the customer form. Do not "
                        "type a custom unit price to bypass the pricelist unless the order is "
                        "tagged 'manual price' and a manager has approved."
                    ),
                ),
                (
                    "Invoicing policy",
                    (
                        "The company default invoicing policy is ordered quantities. Project-based "
                        "customers may be switched to delivered quantities on the product form. "
                        "Down payments of 30% are required for orders above 20,000 USD before "
                        "the first delivery is released."
                    ),
                ),
            ],
        )
    )

    print(f"\nDone. {len(paths)} PDFs in {OUT_DIR}/")
    return paths


if __name__ == "__main__":
    generate_all()
