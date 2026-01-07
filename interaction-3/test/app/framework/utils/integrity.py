import esp32
def run_integrity_checks():
    temp = esp32.raw_temperature()
    print("Current board temp : ",temp)

    if temp > 176:
        raise SystemError("ESP Temperature exceeds 80°C (176.00°F)")