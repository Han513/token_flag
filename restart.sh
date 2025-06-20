#!/bin/bash

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 日誌函數
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 檢查 Docker 是否運行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker 未運行，請先啟動 Docker"
        exit 1
    fi
}

# 檢查 docker-compose 是否可用
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        log_error "docker-compose 未安裝或不在 PATH 中"
        exit 1
    fi
}

# 顯示幫助信息
show_help() {
    echo "使用方法: $0 [命令] [服務]"
    echo ""
    echo "命令:"
    echo "  start    啟動服務"
    echo "  stop     停止服務"
    echo "  restart  重啟服務"
    echo "  rebuild  重建並重啟所有服務"
    echo "  status   查看服務狀態"
    echo "  logs     查看服務日誌"
    echo "  build    重新構建服務"
    echo "  help     顯示此幫助信息"
    echo ""
    echo "服務:"
    echo "  kol_scheduler    KOL 爬蟲定時任務"
    echo "  token_crawler    代幣信息爬蟲"
    echo "  all              所有服務"
    echo ""
    echo "示例:"
    echo "  $0 start all                    # 啟動所有服務"
    echo "  $0 restart kol_scheduler        # 重啟 KOL 定時任務"
    echo "  $0 logs token_crawler           # 查看代幣爬蟲日誌"
    echo "  $0 status                       # 查看所有服務狀態"
}

# 啟動服務
start_service() {
    local service=$1
    log_info "啟動服務: $service"
    
    if [ "$service" = "all" ]; then
        docker-compose up -d
    else
        docker-compose up -d "$service"
    fi
    
    if [ $? -eq 0 ]; then
        log_info "服務啟動成功"
        sleep 2
        show_status
    else
        log_error "服務啟動失敗"
        exit 1
    fi
}

# 停止服務
stop_service() {
    local service=$1
    log_info "停止服務: $service"
    
    if [ "$service" = "all" ]; then
        docker-compose down
    else
        docker-compose stop "$service"
    fi
    
    if [ $? -eq 0 ]; then
        log_info "服務停止成功"
    else
        log_error "服務停止失敗"
        exit 1
    fi
}

# 重啟服務
restart_service() {
    local service=$1
    log_info "重啟服務: $service"
    
    if [ "$service" = "all" ]; then
        docker-compose down
        sleep 2
        docker-compose up -d
    else
        docker-compose restart "$service"
    fi
    
    if [ $? -eq 0 ]; then
        log_info "服務重啟成功"
        sleep 2
        show_status
    else
        log_error "服務重啟失敗"
        exit 1
    fi
}

# 查看服務狀態
show_status() {
    log_info "服務狀態:"
    echo ""
    docker-compose ps
    echo ""
    
    # 檢查容器健康狀態
    for container in $(docker-compose ps -q); do
        if [ -n "$container" ]; then
            container_name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/\///')
            status=$(docker inspect --format='{{.State.Status}}' "$container")
            health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "N/A")
            
            if [ "$status" = "running" ]; then
                log_info "$container_name: 運行中 (健康狀態: $health)"
            else
                log_warn "$container_name: $status"
            fi
        fi
    done
}

# 查看服務日誌
show_logs() {
    local service=$1
    
    if [ "$service" = "all" ]; then
        log_info "查看所有服務日誌 (按 Ctrl+C 退出)"
        docker-compose logs -f
    else
        log_info "查看 $service 日誌 (按 Ctrl+C 退出)"
        docker-compose logs -f "$service"
    fi
}

# 重新構建服務
build_service() {
    local service=$1
    log_info "重新構建服務: $service"
    
    if [ "$service" = "all" ]; then
        docker-compose build --no-cache
    else
        docker-compose build --no-cache "$service"
    fi
    
    if [ $? -eq 0 ]; then
        log_info "服務構建成功"
    else
        log_error "服務構建失敗"
        exit 1
    fi
}

# 主函數
main() {
    # 檢查環境
    check_docker
    check_docker_compose
    
    # 切換到腳本目錄
    cd "$SCRIPT_DIR"
    
    # 解析參數
    local command=$1
    local service=$2

    # 如果只輸入服務名，默認為重啟該服務
    if [[ "$command" == "kol_scheduler" || "$command" == "token_crawler" ]]; then
        restart_service "$command"
        exit 0
    fi

    case $command in
        "start")
            start_service "$service"
            ;;
        "stop")
            stop_service "$service"
            ;;
        "restart")
            restart_service "$service"
            ;;
        "rebuild")
            build_service all
            restart_service all
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$service"
            ;;
        "build")
            build_service "$service"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        ""|'' )
            # 無參數時預設執行 rebuild
            log_info "未指定指令，預設執行 rebuild（重建並重啟所有服務）"
            build_service all
            restart_service all
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 執行主函數
main "$@" 