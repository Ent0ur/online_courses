import matplotlib.pyplot as plt

def create_bar_chart(labels, values, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(labels, values)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

def create_pie_chart(values, labels, title):
    fig, ax = plt.subplots(figsize=(6,4))
    ax.pie(values, labels=labels, autopct='%1.1f%%')
    ax.set_title(title)
    return fig

def create_line_chart(x, y, title, xlabel, ylabel):
    """Создаёт линейный график"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, marker='o', linewidth=2, markersize=8)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig