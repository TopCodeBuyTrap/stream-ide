import queue

from APP_SUB_Funcitons import controlar_altura


def Previews(st,_,linguagem,msg_fim_cod):
	col1, col2 = st.columns([1, 30])
	with col1:
		altura_prev = controlar_altura(st, "Preview", altura_inicial=400, passo=300, maximo=800, minimo=200)

	with col2.container(height=altura_prev):
		output_placeholder = st.empty()
		# Processa mensagens da fila
		if _.thread_running:
			new_data = False
			try:
				while True:
					msg = _.output_queue.get_nowait()
					if msg == "PROGRAM_FINISHED":
						_.thread_running = False
						_.output += msg_fim_cod
						new_data = True
						break
					_.output += msg
					new_data = True
			except queue.Empty:
				pass

			if new_data:
				output_placeholder.code(_.output, linguagem, wrap_lines=True, height=altura_prev)
			else:
				st.code(_.output, linguagem, wrap_lines=True, height=altura_prev)
		else:
			st.code(_.output, linguagem, wrap_lines=True, height=altura_prev)

		# Input do usuário (apenas quando executando)
		# Input do usuário (apenas quando executando)
		if _.thread_running:
			user_input = st.chat_input("Digite sua entrada aqui: ")
			if user_input:
				_.input_queue.put(user_input)
				_.output += f"> {user_input}\n"
				st.rerun()
		st.write('')
		st.write('')