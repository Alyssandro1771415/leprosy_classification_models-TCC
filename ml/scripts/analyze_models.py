#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analisador interativo de modelos treinados."""

import glob
import os

from leprosy_ml.evaluation.analysis import (
    analyze_model,
    load_model_with_history,
    plot_training_history,
    print_model_summary,
)
from leprosy_ml.paths import get_ml_root, models_dir

ml_root = get_ml_root()


def find_available_models():
    """Encontra modelos .keras em artifacts/models/."""
    names = set()
    for dataset in ("co2wounds", "atlas"):
        for path in models_dir(dataset).glob("*.keras"):
            names.add(path.stem)
    return sorted(names)


def display_header():
    print("🔍 ANALISADOR DE MODELOS DE HANSENÍASE")
    print("=" * 60)
    print("📊 Análise completa de modelos treinados")
    print("📈 Métricas, histórico e informações do dataset")
    print("=" * 60)


def display_model_menu(available_models):
    print(f"\n📁 MODELOS DISPONÍVEIS ({len(available_models)} encontrados):")
    print("-" * 40)

    if not available_models:
        print("❌ Nenhum modelo encontrado em artifacts/models/")
        print("   Execute o treinamento primeiro!")
        return None

    for i, model_name in enumerate(available_models, 1):
        history_exists = any(
            (models_dir(d) / f"{model_name}_history.pkl").is_file() for d in ("co2wounds", "atlas")
        )
        info_exists = any(
            (models_dir(d) / f"{model_name}_info.pkl").is_file() for d in ("co2wounds", "atlas")
        )
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
            if choice == str(len(available_models) + 1):
                return "all"
            if 1 <= int(choice) <= len(available_models):
                return available_models[int(choice) - 1]
            print("❌ Opção inválida! Tente novamente.")
        except (ValueError, IndexError):
            print("❌ Entrada inválida! Digite um número.")


def analyze_single_model(model_name):
    print(f"\n{'=' * 60}")
    print(f"🔍 ANALISANDO: {model_name.upper()}")
    print(f"{'=' * 60}")

    try:
        model, history, dataset_info = load_model_with_history(model_name)
        if model is None:
            print(f"❌ Erro: Não foi possível carregar o modelo '{model_name}'")
            return False

        print_model_summary(model, history, dataset_info, model_name)
        if history:
            print("\n📊 Gerando gráficos de treinamento...")
            plot_training_history(history, model_name)
        else:
            print("\n⚠️ Histórico de treinamento não disponível para gráficos")

        print(f"\n✅ Análise de '{model_name}' concluída!")
        return True
    except Exception as e:
        print(f"❌ Erro ao analisar '{model_name}': {e}")
        return False


def analyze_all_models(available_models):
    print(f"\n{'=' * 60}")
    print(f"🔍 ANALISANDO TODOS OS MODELOS ({len(available_models)})")
    print(f"{'=' * 60}")

    successful = 0
    for i, model_name in enumerate(available_models, 1):
        print(f"\n[{i}/{len(available_models)}] Processando: {model_name}")
        if analyze_single_model(model_name):
            successful += 1
        if i < len(available_models):
            input("\n⏸️ Pressione ENTER para continuar para o próximo modelo...")

    print(f"\n✅ Modelos analisados com sucesso: {successful}/{len(available_models)}")


def main():
    os.chdir(ml_root)
    display_header()
    available_models = find_available_models()

    while True:
        choice = display_model_menu(available_models)
        if choice == "exit":
            print("\n👋 Encerrando análise. Até logo!")
            break
        if choice == "all":
            analyze_all_models(available_models)
        elif choice:
            analyze_single_model(choice)
        else:
            break

        if choice != "exit":
            print(f"\n{'=' * 60}")
            cont = input("🔄 Deseja analisar outro modelo? (s/N): ").strip().lower()
            if cont not in ["s", "sim", "y", "yes"]:
                print("\n👋 Encerrando análise. Até logo!")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Análise interrompida pelo usuário.")
