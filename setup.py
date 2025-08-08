#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para o projeto de Classificação de Hanseníase
"""

import os
import sys
import subprocess

def print_header():
    """Exibe cabeçalho do setup"""
    print("🏥 SETUP - Modelos de Classificação de Hanseníase")
    print("=" * 60)
    print("🔧 Configurando ambiente de desenvolvimento...")
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

def create_virtual_environment():
    """Cria ambiente virtual se não existir"""
    print("\n🔧 Configurando ambiente virtual...")
    
    if os.path.exists('venv'):
        print("✅ Ambiente virtual já existe")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Ambiente virtual criado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao criar ambiente virtual")
        return False

def install_dependencies():
    """Instala dependências do requirements.txt"""
    print("\n📦 Instalando dependências...")
    
    # Determina o comando pip baseado no SO
    if os.name == 'nt':  # Windows
        pip_cmd = 'venv\\Scripts\\pip'
    else:  # Linux/Mac
        pip_cmd = 'venv/bin/pip'
    
    try:
        # Atualiza pip
        subprocess.run([pip_cmd, 'install', '--upgrade', 'pip'], check=True)
        print("✅ pip atualizado")
        
        # Instala dependências
        subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando estrutura de diretórios...")
    
    directories = [
        'models',
        'data/raw/train_images_binary',
        'data/raw/train_images_classification',
        'data/processed/train_images_binary',
        'data/processed/train_images_classification'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}")
    
    return True

def show_next_steps():
    """Mostra próximos passos"""
    print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("📋 Próximos passos:")
    print()
    
    if os.name == 'nt':  # Windows
        print("1. Ativar ambiente virtual:")
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("1. Ativar ambiente virtual:")
        print("   source venv/bin/activate")
    
    print()
    print("2. Adicionar suas imagens:")
    print("   - Imagens originais em: data/raw/")
    print("   - Execute pré-processamento se necessário")
    print()
    print("3. Treinar modelos:")
    print("   python train/binary_model_from_zero.py")
    print("   python train/classsification_model_from_zero.py")
    print()
    print("4. Analisar resultados:")
    print("   python analyze_models.py")
    print()
    print("📚 Documentação:")
    print("   - README.md - Guia principal")
    print("   - README_ANALYSIS.md - Guia de análise")
    print("   - TECHNICAL_DETAILS.md - Detalhes técnicos")
    print()
    print("🚀 Projeto pronto para uso!")

def main():
    """Função principal do setup"""
    print_header()
    
    # Verificações e configurações
    if not check_python_version():
        sys.exit(1)
    
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
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
