class Chatbot:
    def __init__(self):
        self.num_turn_history = 3


    def get_response(self, user_response='', history_context='', history_reply=''):
        # Note : history_context & history_reply : collections.deque
        history_context_text = ""
        if (len(history_context) >= self.num_turn_history):
            for i in range(self.num_turn_history):
                history_context_text += history_context[len(history_context) + i - self.num_turn_history] + " "

        history_reply_text = ""
        if (len(history_reply) >= self.num_turn_history):
            for i in range(self.num_turn_history):
                history_reply_text += history_reply[len(history_reply) + i - self.num_turn_history] + " "

        reply = 'Hi! This is sample response.' # put your chatbot in here

        return reply


if __name__ == "__main__":
    Chatbot = Chatbot()
    while True:
        print(rule.get_reply(input('type your mesesage : '), [],[]))
