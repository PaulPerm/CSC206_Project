class Reports:

    SALES_PRODUCTIVITY_QUERY = """
        SELECT 
            u.first_name,
            u.last_name,
            COUNT(st.sales_transactionID) AS vehicles_sold,
            SUM(pt.purchase_price * 1.4 + IFNULL(SUM_PARTS.total_parts_cost * 1.2, 0)) AS total_sales_price,
            ROUND(AVG(pt.purchase_price * 1.4 + IFNULL(SUM_PARTS.total_parts_cost * 1.2, 0)), 2) AS avg_sales_price
        FROM salestransactions st
        JOIN users u ON u.userID = st.userID
        JOIN purchasetransactions pt ON pt.vehicleID = st.vehicleID
        LEFT JOIN (
            SELECT 
                po.vehicleID,
                SUM(p.cost * p.quantity) AS total_parts_cost
            FROM partorders po
            JOIN parts p ON p.part_orderID = po.part_orderID
            GROUP BY po.vehicleID
        ) AS SUM_PARTS ON SUM_PARTS.vehicleID = pt.vehicleID
        GROUP BY u.userID
        ORDER BY vehicles_sold DESC, total_sales_price DESC;
    """

    SELLER_HISTORY_QUERY = """
        SELECT 
            c.first_name,
            c.last_name,
            COUNT(pt.purchase_transactionID) AS vehicles_sold_to_geneva,
            SUM(pt.purchase_price) AS total_paid
        FROM purchasetransactions pt
        JOIN customers c ON c.customerID = pt.customerID
        GROUP BY c.customerID
        ORDER BY vehicles_sold_to_geneva DESC, total_paid ASC;
    """

    PART_STATISTICS_QUERY = """
        SELECT 
            v.vendor_name,
            COUNT(p.partID) AS total_parts_purchased,
            SUM(p.cost * p.quantity) AS total_spent,
            ROUND(AVG(p.cost), 2) AS avg_part_cost
        FROM vendors v
        JOIN partorders po ON po.vendorID = v.vendorID
        JOIN parts p ON p.part_orderID = po.part_orderID
        GROUP BY v.vendorID
        ORDER BY total_parts_purchased DESC;
    """
