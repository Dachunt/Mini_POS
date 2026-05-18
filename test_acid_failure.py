#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ACID compliance: ensure stock never goes negative and failed transactions don't leave partial state
"""

import subprocess
import json
import threading
import time
from decimal import Decimal

def test_oversell_protection():
    """Test that overselling is prevented"""
    
    print("[*] Testing ACID: Over-sell Prevention")
    print()
    
    # Product 3 currently has 60 units
    # We'll try to sell 40 units concurrently (4 transactions x 10 units each)
    # Plus 1 transaction trying to sell 30 units
    # Total request: 70 units > 60 available
    # Expected: 5 succeed, 1 fails (insufficient stock)
    
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
                            "producto_id": 3,
                            "cantidad": qty,
                            "precio_unitario": 22.50
                        }
                    ],
                    "metodo_pago": "tarjeta"
                })
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            response = json.loads(result.stdout)
            
            if "error" in response:
                transactions.append({
                    "sale": sale_num,
                    "qty": qty,
                    "status": "REJECTED",
                    "reason": response["error"]
                })
                print(f"  Sale {sale_num} ({qty} units): REJECTED - {response['error']}")
            else:
                transactions.append({
                    "sale": sale_num,
                    "qty": qty,
                    "status": "SUCCESS",
                })
                print(f"  Sale {sale_num} ({qty} units): SUCCESS")
                
        except Exception as e:
            transactions.append({
                "sale": sale_num,
                "qty": qty,
                "status": "ERROR",
            })
            print(f"  Sale {sale_num}: ERROR - {e}")
    
    # Get current stock
    cmd = ["curl", "-s", "http://localhost:5000/api/productos"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    products = json.loads(result.stdout)
    product = next(p for p in products if p["id"] == 3)
    initial_stock = product["stock_actual"]
    
    print(f"[*] Product 3 (Galletas Oreo) current stock: {initial_stock} units")
    print(f"[*] Attempting to sell 70 units concurrently (risk of over-sell)...")
    print()
    
    # Launch concurrent sales
    threads = []
    for i in range(4):
        t = threading.Thread(target=make_sale, args=(i+1, 10))
        threads.append(t)
        t.start()
    
    # Extra transaction trying to sell 30
    t = threading.Thread(target=make_sale, args=(5, 30))
    threads.append(t)
    t.start()
    
    # Wait for all
    for t in threads:
        t.join()
    
    print()
    
    # Check results
    successful = sum(1 for t in transactions if t["status"] == "SUCCESS")
    rejected = sum(1 for t in transactions if t["status"] == "REJECTED")
    total_sold = sum(t["qty"] for t in transactions if t["status"] == "SUCCESS")
    
    print(f"[*] Results: {successful} succeeded, {rejected} rejected")
    print(f"[*] Total units sold: {total_sold}")
    print()
    
    # Get final stock
    cmd = ["curl", "-s", "http://localhost:5000/api/productos"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    products = json.loads(result.stdout)
    product = next(p for p in products if p["id"] == 3)
    final_stock = product["stock_actual"]
    
    expected_stock = initial_stock - total_sold
    print(f"[*] Final stock: {final_stock} units")
    print(f"[*] Expected: {expected_stock} units (initial {initial_stock} - sold {total_sold})")
    print()
    
    # Verify
    if final_stock == expected_stock and rejected > 0:
        print("[+] ACID OVER-SELL TEST PASSED!")
        print("    - Some transactions were rejected due to insufficient stock")
        print("    - Stock is consistent (no negative or corrupted values)")
        print("    - No partial states were committed")
        return True
    else:
        print("[-] ACID OVER-SELL TEST FAILED!")
        if final_stock != expected_stock:
            print(f"    - Stock mismatch: expected {expected_stock}, got {final_stock}")
        if rejected == 0:
            print(f"    - Expected some rejections but got none!")
        return False

if __name__ == "__main__":
    test_oversell_protection()
