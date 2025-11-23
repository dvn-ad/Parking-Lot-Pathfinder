import time
import matplotlib.pyplot as plt
import numpy as np
from program import load_floors, find_best_slot

def run_analysis():
    print("Memuat data lantai...")
    floors = load_floors("maps")
    
    # Konfigurasi Multiple Test Cases
    test_cases = [
        {
            "name": "Case 1: Reguler (Lt 10)\nPrefer Car",
            "target_symbol": "P",
            "desired_floor": 10,
            "w_lobby": 1,
            "w_car": 5
        },
        {
            "name": "Case 2: Ladies (Lt 9)\nPrefer Lobby",
            "target_symbol": "L",
            "desired_floor": 9,
            "w_lobby": 5,
            "w_car": 1
        },
        {
            "name": "Case 3: Disability (Lt 0)\nBalanced",
            "target_symbol": "D",
            "desired_floor": 0,
            "w_lobby": 1,
            "w_car": 1
        },
        {
            "name": "Case 4: Normal (Lt 5)\nPrefer Lobby",
            "target_symbol": "P",
            "desired_floor": 5,
            "w_lobby": 5,
            "w_car": 1
        },
        {
            "name": "Case 5: Disability (Lt 2)\nPrefer Car",
            "target_symbol": "D",
            "desired_floor": 2,
            "w_lobby": 1,
            "w_car": 5
        },
        {
            "name": "Case 6: Ladies (Lt 8)\nPrefer Car",
            "target_symbol": "L",
            "desired_floor": 8,
            "w_lobby": 1,
            "w_car": 5
        },
        {
            "name": "Case 7: Normal (Lt 3)\nBalanced",
            "target_symbol": "P",
            "desired_floor": 3,
            "w_lobby": 1,
            "w_car": 1
        },
        {
            "name": "Case 8: Disability (Lt 0)\nPrefer Lobby",
            "target_symbol": "D",
            "desired_floor": 0,
            "w_lobby": 5,
            "w_car": 1
        },
        {
            "name": "Case 9: Normal (Lt 11)\nPrefer Car",
            "target_symbol": "P",
            "desired_floor": 11,
            "w_lobby": 1,
            "w_car": 5
        },
        {
            "name": "Case 10: Ladies (Lt 4)\nBalanced",
            "target_symbol": "L",
            "desired_floor": 4,
            "w_lobby": 1,
            "w_car": 1
        }
    ]
    
    algorithms = ["a_star", "dijkstra", "bfs", "greedy_bfs"]
    algo_labels = ["A*", "Dijkstra", "BFS", "Greedy BFS"]
    
    # Penyimpanan hasil: results[algo] = [val_case1, val_case2, ...]
    results_time = {algo: [] for algo in algorithms}
    results_cost = {algo: [] for algo in algorithms}
    results_visited = {algo: [] for algo in algorithms}
    
    case_names = [case["name"] for case in test_cases]

    for case in test_cases:
        print(f"\nRunning Analysis for: {case['name'].replace(chr(10), ' ')}")
        print(f"{'Algoritma':<15} | {'Waktu (detik)':<15} | {'Total Cost':<15} | {'Node Dikunjungi':<15}")
        print("="*70)

        for algo in algorithms:
            start_time = time.time()
            
            try:
                result = find_best_slot(
                    floors, 
                    algo, 
                    case["target_symbol"], 
                    case["desired_floor"], 
                    case["w_lobby"], 
                    case["w_car"]
                )
            except Exception as e:
                print(f"Error running {algo}: {e}")
                result = None

            end_time = time.time()
            exec_time = end_time - start_time
            
            if result:
                best_slot, path_car, path_lobby, score, visited_car, visited_lobby = result
                total_visited = len(visited_car) + len(visited_lobby)
                
                results_time[algo].append(exec_time)
                results_cost[algo].append(score)
                results_visited[algo].append(total_visited)
                
                print(f"{algo:<15} | {exec_time:<15.6f} | {score:<15.2f} | {total_visited:<15}")
            else:
                results_time[algo].append(0)
                results_cost[algo].append(0)
                results_visited[algo].append(0)
                print(f"{algo:<15} | {'GAGAL':<15} | {'-':<15} | {'-':<15}")
            
        print("="*70)
    
    # Visualisasi Hasil
    plot_grouped_comparison(case_names, algorithms, algo_labels, results_time, results_cost, results_visited)

def plot_grouped_comparison(case_labels, algorithms, algo_labels, results_time, results_cost, results_visited):
    x = np.arange(len(case_labels))
    width = 0.2  # Lebar bar
    
    # Membuat 3 subplot vertikal
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 18))
    
    # Helper function untuk plotting
    def plot_metric(ax, data_dict, title, ylabel):
        multiplier = 0
        for i, algo in enumerate(algorithms):
            offset = width * multiplier
            values = data_dict[algo]
            rects = ax.bar(x + offset, values, width, label=algo_labels[i])
            # ax.bar_label(rects, padding=3, fmt='%.2f', fontsize=8) # Optional: label di atas bar
            multiplier += 1

        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x + width * (len(algorithms) - 1) / 2)
        ax.set_xticklabels(case_labels, rotation=15, ha='center', fontsize=9)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(axis='y', linestyle='--', alpha=0.7)

    plot_metric(ax1, results_time, 'Perbandingan Waktu Eksekusi', 'Waktu (detik)')
    plot_metric(ax2, results_cost, 'Perbandingan Total Cost (Skor)', 'Cost')
    plot_metric(ax3, results_visited, 'Perbandingan Node yang Dikunjungi', 'Jumlah Node')

    plt.tight_layout()
    plt.savefig('analisis_multi_case.png')
    print("\nGrafik telah disimpan sebagai 'analisis_multi_case.png'")
    plt.show()

if __name__ == "__main__":
    # Pastikan library yang dibutuhkan terinstall
    try:
        import matplotlib
        import numpy
    except ImportError as e:
        print("Library visualisasi belum terinstall.")
        print(f"Error: {e}")
        print("Silakan install dengan menjalankan: pip install matplotlib numpy")
        exit()
        
    run_analysis()
