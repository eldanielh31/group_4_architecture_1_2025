all: encrypt decrypt compare

encrypt:
	python3 main_encrypt_file.py test_input.txt salida.enc

decrypt:
	python3 main_decrypt_file.py salida.enc salida_descifrada.txt

compare:
	diff test_input.txt salida_descifrada.txt && echo "Archivos coinciden" || echo "Archivos diferentes"

test:
	python3 main.py

clean:
	rm -f salida.enc salida_descifrada.txt
