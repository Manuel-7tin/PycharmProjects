import os
import fnmatch

def get_files_by_extension(directory, extension):
	"""Returns a list of files matching the extension in the directory."""
	return [f for f in os.listdir(directory) if fnmatch.fnmatch(f, f"*{extension}")]

# Example usage
files = get_files_by_extension("./chat-details", ".txt")
print(files)
file = None
for a_file in files:
	if a_file[:8] == "WhatsApp":
		file = a_file
		break

if len(files) < 1 or not file:
	print("raise error file not found")
	exit(500)
with open(f"./chat-details/{file}", mode="r", encoding="utf-8") as txtfile:
	txt_content = txtfile.readlines()
print('WhatsApp Chat'[:8])

def organize_msgs(msg_list: list) -> list:
	stopped = 0
	repeat = False
	msg_list = msg_list.copy()
	while True:
		for i in range(len(msg_list)):
			if i < stopped:
				continue
			if not msg_list[i][0].isdigit():
				if i == 0:
					print("raise error 5-something")
				added = msg_list[i-1] + " " + msg_list[i]
				msg_list[i-1] = added
				msg_list.pop(i)
				stopped = i
				repeat = True
				break
			repeat = False
		if repeat:
			continue
		break
	return msg_list

print(len(txt_content))
new = organize_msgs(txt_content)
print(len(new))
print("oioi")

def caution_split(text: str, delimiter: str) -> list:
	text_details = text.split(delimiter)
	if len(text_details) > 2:
		second_part = ""
		for j in range(len(text_details)):
			if j == 0:
				continue
			second_part += text_details[j] + delimiter
		text_details = [text_details[0], second_part]
	return text_details

def parse_chat(messages: list) -> dict:
	parsed_chat = {}
	for i in messages:
		temp_list = caution_split(i, " - ")
		date, time = temp_list[0].split(", ")
		name, msg_body = caution_split(temp_list[1], ": ")
		if "(file attached)" in msg_body:
			msg_type = "text"
		elif msg_body[:3] == "STK":
			msg_type = "sticker"
		elif msg_body[:3] == "IMG":
			msg_type = "image"
		elif msg_body[:3] == "PTT":
			msg_type = "audio"
		elif msg_body[:3] == "VID":
			msg_type = "video"
		elif ".vcf" in msg_body:
			msg_type = "contact"
		else:
			msg_type = "text"

		if msg_type != "text":
			msg_body = msg_body.removesuffix("(file attached)").strip(" ")
		edited = True if "<This message was edited>" in msg_body else False
		#"contact, video, vn/audio, image, sticker, text"
		print(date)
		print(time)
		print(name)
		print(msg_body)