#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ACID compliance: concurrent transactions trying to reduce stock of same product
"""

import subprocess
import json
import threading
import time
from decimal import Decimal

def test_concurrent_sales():
    """Test that concurrent transactions don't corrupt data"""
    
    print("[*] Testing ACID compliance with concurrent transactions...")
    print("[*] Product 4 (Agua Bonafont) initially has 120 units")
    print()
    
    # Product 4 has 120 units
    # We'll try to sell 100 units concurrently (10 transactions x 10 units each)
    # This should succeed (120 >= 100)
    
    transactions = []
    
    def make_sale(sale_num, qty):
        """Execute a single sale"""
        try:
            cmd = [
                "curl", "-s", "-X", "POST", 
                "http://localhost:5000/api/ventas",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "items": [
                        {
                            "producto_id": 4,
                            "cantidad": qty,
                            "precio_unitario": 12.00
                        }
                    ],
                    "metodo_pago": "efectivo"
                })
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            response = json.loads(result.stdout)
            
            if "error" in response:
                transactions.append({
                    "sale": sale_num,
                    "qty": qty,
                    "status": "FAILED",
                    "error": response["error"]
                })
                print(f"  Sale {sale_num}: FAILED - {response['error']}")
            else:
                transactions.append({
                    "sale": sale_num,
                    "qty": qty,
                    "status": "SUCCESS",
                    "venta_id": response.get("id")
                })
                print(f"  Sale {sale_num}: SUCCESS (Total: {response['total']})")
                
        except Exception as e:
            transactions.append({
                "sale": sale_num,
                "qty": qty,
                "status": "ERROR",
                "error": str(e)
            })
            print(f"  Sale {sale_num}: ERROR - {e}")
    
    # Launch 10 concurrent sales
    print("[*] Launching 10 concurrent sales of 10 units each...")
    threads = []
    for i in range(10):
        t = threading.Thread(target=make_sale, args=(i+1, 10))
        threads.append(t)
        t.start()
    
    # Wait for all to complete
    for t in threads:
        t.join()
    
    print()
    print("[*] All transactions completed")
    print()
    
    # Check results
    successful = sum(1 for t in transactions if t["status"] == "SUCCESS")
    failed = sum(1 for t in transactions if t["status"] == "FAILED")
    
    print(f"[*] Results: {successful} successful, {failed} failed")
    print()
    
    # Get final stock
    cmd = ["curl", "-s", "http://localhost:5000/api/productos"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    products = json.loads(result.stdout)
    
    agua = next(p for p in products if p["id"] == 4)
    final_stock = agua["stock_actual"]
    
    print(f"[*] Final stock of Product 4: {final_stock} units")
    print(f"    Expected: 20 (120 - 100)")
    print()
    
    if final_stock == 20 and successful == 10:
        print("[+] ACID TEST PASSED!")
        print("    - All 10 transactions succeeded")
        print("    - Stock is consistent and correct")
        return True
    else:
        print("[-] ACID TEST FAILED!")
        if final_stock != 20:
            print(f"    - Stock mismatch: expected 20, got {final_stock}")
        if successful != 10:
            print(f"    - Some transactions failed: {successful}/10 succeeded")
        return False

if __name__ == "__main__":
    test_concurrent_sales()
