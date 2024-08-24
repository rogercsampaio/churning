import streamlit as st
import sklearn
import pickle
import pandas as pd
# Cabeçalho
#st.image("images/logo.PNG")
st.title("Telecom CHURN")
st.info('Objetivo: prever a rotatividade(probabilidade de cancelar o contrato) de um cliente na operadora utilizando dados históricos de custos de ligações efetuadas no período, total de ligações ao call center,estado,código de área entre outras informações.',icon="ℹ️")
# Carregando bases de dados principais
try:
    cli_contratos_abt = pd.read_csv("bases/abt_contratos_clientes.csv")

    # Será usada para tratamento de algumas variáveis
    previsoes = pd.read_csv("bases/cli_contratos_previsoes_final.csv")
except Exception as excecao:
    st.markdown("Erro ao carregar a base de dados")
    st.markdown("Não é possível prosseguir com a aplicação. Contrate o administrador.")
else:
    st.markdown("Base de dados carregada.")
    
    # Carregando modelo preditivo
    try:
        with open('code/modelagem/random_forest_modelo_v1.pkl', 'rb') as f:
            random_forest_modelo_carregado = pickle.load(f)
    except Exception as excecao:
        st.markdown(excecao)
        #st.markdown("Erro ao carregar o modelo preditivo")
    else:
        st.markdown("Modelo carregado.")    

    # Preenchimentos de campos
    st.header("Cadastro")

    # Estado
    opcao_estado = st.selectbox(
        "Qual o estado",
        cli_contratos_abt['State'].unique(),
    )
    st.write("Estado selecionado: ", opcao_estado)

    # Tempo de conta em anos
    opcao_tempo_anos_conta = st.slider("Quanto tempo tem de conta em anos?", min(cli_contratos_abt['Account_length_year']), max(cli_contratos_abt['Account_length_year']))
    st.write("Tempo selecionado em anos: ",opcao_tempo_anos_conta)

    # Área de código
    opcao_codigo_area = st.selectbox(
        "Qual a área de código?",
        cli_contratos_abt['Area code'].unique(),
    )
    st.write("Área de código selecionada: ", opcao_codigo_area)


    # Suporte ao plano internacional ou não
    opcao_suporte_plano_inter = st.checkbox("Tem suporte ao plano internacional?")
    #st.write("Suporte ao plano internacional? ", opcao_suporte_plano_inter)

    # Suporte ao vmail
    opcao_suporte_plano_correio_voz = st.checkbox("Tem suporte ao plano de correio de voz?")
    #st.write("Suporte ao plano de correio de voz? ", opcao_suporte_plano_correio_voz)

    # Número de mensagens vmail consumido
    opcao_num_vmail_message = st.slider("Qual foi o número de mensagens vmail consumido no período? ", min(cli_contratos_abt['Number vmail messages']), max(cli_contratos_abt['Number vmail messages']))
    st.write("Número de mensagens vmail consumido no período: ",opcao_num_vmail_message)

    # Taxa total do dia
    opcao_taxa_diaria = st.slider("Qual foi a taxa total do dia?", min(cli_contratos_abt['Total day charge']), max(cli_contratos_abt['Total day charge']))
    st.write("Taxa total do dia: ",opcao_taxa_diaria)

    # Taxa total das ligações vespertinas
    opcao_taxa_ligacoes_vespertinas = st.slider("Qual foi a taxa total de ligações vespertinas?", min(cli_contratos_abt['Total eve charge']), max(cli_contratos_abt['Total eve charge']))
    st.write("Taxa total das ligações vespertinas: ",opcao_taxa_ligacoes_vespertinas)
    
    # Taxa total das ligações noturnas
    opcao_taxa_ligacoes_noturnas = st.slider("Qual foi a taxa total de ligações noturnas?", min(cli_contratos_abt['Total night charge']), max(cli_contratos_abt['Total night charge']))
    st.write("Taxa total das ligações noturnas: ",opcao_taxa_ligacoes_noturnas)
    
    # Taxa total das ligações gerais
    opcao_taxa_ligacoes_geral = st.slider("Qual foi a taxa total de ligações gerais?", min(cli_contratos_abt['Total intl charge']), max(cli_contratos_abt['Total intl charge']))
    st.write("Taxa total das ligações: ",opcao_taxa_ligacoes_geral)
    
    # Número de chamadas ao call center
    opcao_ligacoes_call_center = st.slider("Qual foi o número de ligações ao call center", min(cli_contratos_abt['Customer service calls']), max(cli_contratos_abt['Customer service calls']))
    st.write("Número de ligações ao call center: ",opcao_ligacoes_call_center)
    
    # Tratamento de valores para a inferência final
    dados_inferir_cliente = previsoes.drop(columns = 'Previsao')
    dados_inferir_cliente = dados_inferir_cliente.head(1) # Uma única coluna
    
    if(opcao_suporte_plano_inter):
        dados_inferir_cliente['International plan_No'] = False
        dados_inferir_cliente['International plan_Yes'] = True
    else:
        dados_inferir_cliente['International plan_No'] = True
        dados_inferir_cliente['International plan_Yes'] = False
        
    if(opcao_suporte_plano_correio_voz):
        dados_inferir_cliente['Voice mail plan_No'] = False
        dados_inferir_cliente['Voice mail plan_Yes'] = True
    else:
        dados_inferir_cliente['Voice mail plan_No'] = True
        dados_inferir_cliente['Voice mail plan_Yes'] = False   
    
    # Definindo para valores zerados
    dados_inferir_cliente['Area code_408'] = False
    dados_inferir_cliente['State_LA'] = False
    
    if(opcao_codigo_area == 415):
       dados_inferir_cliente['Area code_415'] = True
    elif(opcao_codigo_area == 408): 
        dados_inferir_cliente['Area code_408'] = True
    else:
        dados_inferir_cliente['Area code_510'] = True
      
    # Adicionando um prefiro ao estado selecionado
    opcao_estado_prefixado = "State_" + opcao_estado
    dados_inferir_cliente[opcao_estado_prefixado] = True
    
    dados_inferir_cliente['Account_length_year'] = opcao_tempo_anos_conta
    dados_inferir_cliente['Number vmail messages'] = opcao_num_vmail_message
    dados_inferir_cliente['Total day charge'] = opcao_taxa_diaria
    dados_inferir_cliente['Total eve charge'] = opcao_taxa_ligacoes_vespertinas
    dados_inferir_cliente['Total night charge'] = opcao_taxa_ligacoes_noturnas
    dados_inferir_cliente['Total intl charge'] = opcao_taxa_ligacoes_geral
    dados_inferir_cliente['Customer service calls'] = opcao_ligacoes_call_center
    st.write("Dados: ",dados_inferir_cliente)
   
    # Previsão
    st.header("Principais motivos de cancelamento")
    st.markdown("1 - Total de custos de ligações")
    st.markdown("2 - Total de ligações ao call center")
    st.markdown("3 - Total de custos de ligações vespertinas")
    st.markdown("4 - Total de minutos em ligações")
    st.markdown("5 - Não aderência ao plano internacional")
    
    st.header("Inferência")
    botao_prever = st.button("Prever", type="primary")
    if (botao_prever):
        st.write("... Efetuando previsão")
        resultado_previsao = random_forest_modelo_carregado.predict(dados_inferir_cliente)
        if(resultado_previsao == 0.0):
          st.balloons()  
          st.write("Seu cliente TENDE A NÃO DEIXAR VOCÊ!")  
        else:
            st.write("Seu cliente TENDE A DEIXAR VOCÊ!")    