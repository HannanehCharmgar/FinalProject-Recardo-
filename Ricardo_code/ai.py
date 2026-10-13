from google import genai
from decouple import config

from logger import ai_log


class AIGemini:
    def __init__(self):
        try:
            ai_log.log("INFO", "Ai connection .... ")
            self.TK_AI = config("GEMINI_API_KEY")
            self.MODEL = config("GEMINI_MODEL")
            __client = genai.Client(api_key=self.TK_AI)
        except Exception as err:
            ai_log.log("ERROR", f"Ai connection: {err}")
            return ""

    def _send(self, text: str):
        try:
            ai_log.log("INFO", "Send to ai ")
            response = self.__client.models.generate_content(
                model=self.MODEL,
                contents=text,
            )

            re_text = response.text
            return re_text
        except Exception as err:
            ai_log.log("ERROR", f"send and get response of ai: {err}")

    def analysis(self, text: str):
        try:
            re_text = self._send(text=text)

            ai_log.log("INFO", "Start analysis the ai response ... ")
            re_text = re_text[re_text.find("{") : re_text.find("}") + 1 :]
            i_dcot = re_text.find('"', 0)

            data = {}
            while i_dcot != -1:
                key = re_text[i_dcot + 1 : re_text.find('"', i_dcot + 1) :]

                i_dcot = re_text.find('"', re_text.find('"', i_dcot + 1) + 1)

                value = re_text[i_dcot + 1 : re_text.find('"', i_dcot + 1) :]

                i_dcot = re_text.find('"', re_text.find('"', i_dcot + 1) + 1)

                data[key] = value

            return data
        except Exception as err:
            ai_log.log("ERROR", f"Analysis the ai response: {err}")

    def test(self, text: str):
        response = self.__client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=text,
        )

        re_text = response.text
        return re_text
