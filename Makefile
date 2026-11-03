.PHONY: all unit n8 n16 clean
all: unit n8
unit: ; python3 scripts/unit_test_emitters.py
n8:   ; python3 scripts/run_all.py --n 8
n16:  ; python3 scripts/run_all.py --n 16 --min-w 4 --max-segs 3
clean: ; rm -rf build rtl/generated tb/generated
