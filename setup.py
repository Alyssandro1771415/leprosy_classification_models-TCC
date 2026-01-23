#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para o projeto de Classificação de Hanseníase
Usando uv + .venv + uv sync
"""

import os
import sys
import subprocess
import shutil

def print_header():
    """Exibe cabeçalho do setup"""
    print("🏥 SETUP - Modelos de Classificação de Hanseníase")
    print("=" * 60)
    print("⚡ Configurando ambiente com uv (uv sync)...")
    print("=" * 60)

def check_python_version():
    """Verifica versão do Python"""
    print("\n📋 Verificando versão do Python...")

    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        return False

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_uv_installed():
    """Verifica se o uv está instalado"""
    print("\n⚡ Verificando instalação do uv...")

    if shutil.which("uv") is None:
        print("❌ uv não encontrado!")
        print("👉 Instale com:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   ou (Windows): powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        return False

    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ uv encontrado: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao verificar versão do uv")
        return False

def create_virtual_environment():
    """Cria ambiente virtual .venv se não existir"""
    print("\n🔧 Configurando ambiente virtual (.venv)...")

    if os.path.exists(".venv"):
        print("✅ Ambiente virtual .venv já existe")
        return True

    try:
        subprocess.run(
            ["uv", "venv", ".venv"],
            check=True
        )
        print("✅ Ambiente virtual .venv criado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao criar ambiente virtual com uv")
        return False

def sync_dependencies():
    """Sincroniza dependências usando uv sync"""
    print("\n📦 Sincronizando dependências (uv sync)...")

    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml não encontrado!")
        print("👉 uv sync requer um pyproject.toml válido")
        return False

    try:
        subprocess.run(
            ["uv", "sync"],
            check=True
        )
        print("✅ Dependências sincronizadas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao executar uv sync")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando estrutura de diretórios...")

    directories = [
        "models",
        "data/raw/train_images_binary",
        "data/raw/train_images_classification",
        "data/processed/train_images_binary",
        "data/processed/train_images_classification"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}")

    return True

def show_next_steps():
    """Mostra próximos passos"""
    print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("📋 Próximos passos:\n")

    if os.name == "nt":  # Windows
        print("1. Ativar ambiente virtual:")
        print("   .venv\\Scripts\\activate")
    else:  # Linux / macOS
        print("1. Ativar ambiente virtual:")
        print("   source .venv/bin/activate")

    print("\n2. Adicionar suas imagens:")
    print("   - Imagens originais em: data/raw/")
    print("   - Execute pré-processamento se necessário")

    print("\n3. Treinar modelos:")
    print("   python train/binary_model_from_zero.py")
    print("   python train/classsification_model_from_zero.py")

    print("\n4. Analisar resultados:")
    print("   python analyze_models.py")

    print("\n📚 Documentação:")
    print("   - README.md")
    print("   - README_ANALYSIS.md")
    print("   - TECHNICAL_DETAILS.md")

    print("\n🚀 Projeto pronto para uso com uv!")

def main():
    """Função principal do setup"""
    print_header()

    if not check_python_version():
        sys.exit(1)

    if not check_uv_installed():
        sys.exit(1)

    if not create_virtual_environment():
        sys.exit(1)

    if not sync_dependencies():
        sys.exit(1)

    if not create_directories():
        sys.exit(1)

    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado durante o setup: {e}")
        sys.exit(1)
