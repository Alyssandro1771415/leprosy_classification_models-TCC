#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ANALISADOR DE MODELOS TREINADOS
==================================

Este script carrega os modelos salvos na pasta 'models' e apresenta suas métricas,
histórico de treinamento e informações do dataset de forma organizada.

Uso:
    python analyze_models.py

Modelos suportados:
    - modelo_binario_do_zero
    - modelo_classificacao_do_zero
"""

import sys
import os
import glob

# Adiciona o diretório raiz do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from utils.model_analysis import analyze_model, load_model_with_history, plot_training_history, print_model_summary

def find_available_models():
    """
    Encontra todos os modelos disponíveis na pasta models

    Returns:
        list: Lista de nomes de modelos disponíveis
    """
    models_dir = "./models"
    if not os.path.exists(models_dir):
        return []

    # Procura por arquivos .pkl que não sejam history ou info
    model_files = glob.glob(os.path.join(models_dir, "*.pkl"))
    model_names = []

    for file_path in model_files:
        filename = os.path.basename(file_path)
        if not filename.endswith(('_history.pkl', '_info.pkl')):
            model_name = filename.replace('.pkl', '')
            model_names.append(model_name)

    return sorted(model_names)

def display_header():
    """Exibe o cabeçalho do programa"""
    print("🔍 ANALISADOR DE MODELOS DE HANSENÍASE")
    print("=" * 60)
    print("📊 Análise completa de modelos treinados")
    print("📈 Métricas, histórico e informações do dataset")
    print("=" * 60)

def display_model_menu(available_models):
    """
    Exibe menu de modelos disponíveis

    Args:
        available_models (list): Lista de modelos disponíveis

    Returns:
        str: Escolha do usuário
    """
    print(f"\n📁 MODELOS DISPONÍVEIS ({len(available_models)} encontrados):")
    print("-" * 40)

    if not available_models:
        print("❌ Nenhum modelo encontrado na pasta 'models'")
        print("   Execute o treinamento primeiro!")
        return None

    for i, model_name in enumerate(available_models, 1):
        # Verifica se tem histórico e info
        history_exists = os.path.exists(f"./models/{model_name}_history.pkl")
        info_exists = os.path.exists(f"./models/{model_name}_info.pkl")

        status = "✅" if history_exists and info_exists else "⚠️"
        print(f"   {i}. {model_name} {status}")

    print(f"   {len(available_models) + 1}. Analisar TODOS os modelos")
    print(f"   0. Sair")

    print("\n💡 Legenda: ✅ = Completo (modelo + histórico + info) | ⚠️ = Apenas modelo")

    while True:
        try:
            choice = input(f"\n🎯 Escolha uma opção (0-{len(available_models) + 1}): ").strip()

            if choice == "0":
                return "exit"
            elif choice == str(len(available_models) + 1):
                return "all"
            elif 1 <= int(choice) <= len(available_models):
                return available_models[int(choice) - 1]
            else:
                print("❌ Opção inválida! Tente novamente.")
        except (ValueError, IndexError):
            print("❌ Entrada inválida! Digite um número.")

def analyze_single_model(model_name):
    """
    Analisa um único modelo

    Args:
        model_name (str): Nome do modelo a ser analisado
    """
    print(f"\n{'=' * 60}")
    print(f"🔍 ANALISANDO: {model_name.upper()}")
    print(f"{'=' * 60}")

    try:
        # Carrega modelo com histórico e informações
        model, history, dataset_info = load_model_with_history(model_name)

        if model is None:
            print(f"❌ Erro: Não foi possível carregar o modelo '{model_name}'")
            return False

        # Exibe resumo completo
        print_model_summary(model, history, dataset_info, model_name)

        # Plota gráficos se histórico disponível
        if history:
            print(f"\n📊 Gerando gráficos de treinamento...")
            plot_training_history(history, model_name)
        else:
            print(f"\n⚠️ Histórico de treinamento não disponível para gráficos")

        print(f"\n✅ Análise de '{model_name}' concluída!")
        return True

    except Exception as e:
        print(f"❌ Erro ao analisar '{model_name}': {e}")
        return False

def analyze_all_models(available_models):
    """
    Analisa todos os modelos disponíveis

    Args:
        available_models (list): Lista de modelos disponíveis
    """
    print(f"\n{'=' * 60}")
    print(f"🔍 ANALISANDO TODOS OS MODELOS ({len(available_models)})")
    print(f"{'=' * 60}")

    successful_analyses = 0

    for i, model_name in enumerate(available_models, 1):
        print(f"\n[{i}/{len(available_models)}] Processando: {model_name}")

        if analyze_single_model(model_name):
            successful_analyses += 1

        # Pausa entre modelos (exceto no último)
        if i < len(available_models):
            input("\n⏸️ Pressione ENTER para continuar para o próximo modelo...")

    # Resumo final
    print(f"\n{'=' * 60}")
    print(f"📊 RESUMO DA ANÁLISE COMPLETA")
    print(f"{'=' * 60}")
    print(f"✅ Modelos analisados com sucesso: {successful_analyses}/{len(available_models)}")
    print(f"❌ Modelos com erro: {len(available_models) - successful_analyses}/{len(available_models)}")

    if successful_analyses == len(available_models):
        print(f"🎉 Todos os modelos foram analisados com sucesso!")
    elif successful_analyses > 0:
        print(f"⚠️ Alguns modelos apresentaram problemas na análise")
    else:
        print(f"💥 Nenhum modelo pôde ser analisado")

def main():
    """Função principal do programa"""
    # Muda para o diretório do script
    os.chdir(project_root)

    # Exibe cabeçalho
    display_header()

    # Encontra modelos disponíveis
    available_models = find_available_models()

    while True:
        # Exibe menu e obtém escolha
        choice = display_model_menu(available_models)

        if choice == "exit":
            print("\n👋 Encerrando análise. Até logo!")
            break
        elif choice == "all":
            analyze_all_models(available_models)
        elif choice:
            analyze_single_model(choice)
        else:
            break

        # Pergunta se quer continuar
        if choice != "exit":
            print(f"\n{'=' * 60}")
            continue_choice = input("🔄 Deseja analisar outro modelo? (s/N): ").strip().lower()
            if continue_choice not in ['s', 'sim', 'y', 'yes']:
                print("\n👋 Encerrando análise. Até logo!")
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Análise interrompida pelo usuário.")
        print("👋 Até logo!")
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        print("🔧 Verifique se os modelos foram treinados corretamente.")
