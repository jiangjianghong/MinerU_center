#!/bin/bash

# ==========================================
# MinerU Center 部署脚本
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
CONTAINER_NAME="mineru-center"
IMAGE_NAME="mineru-center"
COMPOSE_FILE="docker-compose.yml"

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否运行
check_docker() {
    print_info "检查 Docker 服务状态..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker 未运行，请先启动 Docker 服务"
        exit 1
    fi
    print_success "Docker 服务正常运行"
}

# 检查 Docker Compose 是否可用
check_docker_compose() {
    print_info "检查 Docker Compose..."
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    elif docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        print_error "Docker Compose 未安装"
        exit 1
    fi
    print_success "Docker Compose 可用: $COMPOSE_CMD"
}

# 检查容器是否存在
check_container_exists() {
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# 检查容器是否正在运行
check_container_running() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# 停止并删除旧容器
cleanup_container() {
    print_info "检查是否存在同名容器..."

    if check_container_exists; then
        print_warning "发现已存在的容器: ${CONTAINER_NAME}"

        if check_container_running; then
            print_info "停止正在运行的容器..."
            docker stop ${CONTAINER_NAME}
            print_success "容器已停止"
        fi

        print_info "删除旧容器..."
        docker rm ${CONTAINER_NAME}
        print_success "旧容器已删除"
    else
        print_info "未发现同名容器，跳过清理步骤"
    fi
}

# 构建镜像
build_image() {
    print_info "开始构建 Docker 镜像..."
    $COMPOSE_CMD -f ${COMPOSE_FILE} build --no-cache
    print_success "镜像构建完成"
}

# 启动容器
start_container() {
    print_info "启动容器..."
    $COMPOSE_CMD -f ${COMPOSE_FILE} up -d
    print_success "容器已启动"
}

# 检查服务状态
check_service() {
    print_info "等待服务启动..."
    sleep 5

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8000/api/stats > /dev/null 2>&1; then
            print_success "服务已就绪"
            return 0
        fi
        print_info "等待服务就绪... ($attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    print_error "服务启动超时，请检查日志"
    return 1
}

# 显示服务状态
show_status() {
    echo ""
    echo "=========================================="
    echo -e "${GREEN}部署完成!${NC}"
    echo "=========================================="
    echo ""
    echo "容器状态:"
    docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    echo "访问地址:"
    echo -e "  - Web UI: ${BLUE}http://localhost:8000/ui${NC}"
    echo -e "  - API:    ${BLUE}http://localhost:8000/api${NC}"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker logs -f ${CONTAINER_NAME}"
    echo "  - 停止服务: $COMPOSE_CMD down"
    echo "  - 重启服务: $COMPOSE_CMD restart"
    echo ""
}

# 显示日志
show_logs() {
    print_info "显示容器日志..."
    docker logs -f ${CONTAINER_NAME}
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    $COMPOSE_CMD -f ${COMPOSE_FILE} down
    print_success "服务已停止"
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    $COMPOSE_CMD -f ${COMPOSE_FILE} restart
    print_success "服务已重启"
}

# 显示帮助
show_help() {
    echo "MinerU Center 部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    部署服务 (默认)"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看日志"
    echo "  status    查看状态"
    echo "  build     仅构建镜像"
    echo "  clean     清理容器和镜像（保留数据）"
    echo "  clean-all 清理所有资源（包括数据，危险操作）"
    echo "  help      显示帮助"
    echo ""
}

# 完整部署流程
deploy() {
    echo ""
    echo "=========================================="
    echo "  MinerU Center 部署脚本"
    echo "=========================================="
    echo ""

    check_docker
    check_docker_compose

    # 确保数据目录存在
    mkdir -p data file

    cleanup_container
    build_image
    start_container
    check_service
    show_status
}

# 清理容器和镜像（保留数据）
clean() {
    print_info "清理容器和镜像..."

    check_docker
    check_docker_compose

    # 停止并删除容器（不使用 -v，保留数据卷）
    if check_container_exists; then
        $COMPOSE_CMD -f ${COMPOSE_FILE} down --rmi local
        print_success "容器和镜像已清理"
        print_info "数据目录 (data/, file/) 已保留"
    else
        print_info "没有需要清理的容器"
    fi
}

# 完全清理（包括数据）- 危险操作
clean_all() {
    print_warning "警告: 此操作将删除所有数据，包括数据库!"
    echo -n "确认删除所有数据? (输入 'yes' 确认): "
    read confirm

    if [ "$confirm" != "yes" ]; then
        print_info "操作已取消"
        return 0
    fi

    check_docker
    check_docker_compose

    # 停止并删除容器
    if check_container_exists; then
        $COMPOSE_CMD -f ${COMPOSE_FILE} down --rmi local
    fi

    # 删除数据目录
    if [ -d "data" ]; then
        rm -rf data
        print_success "数据目录已删除"
    fi

    if [ -d "file" ]; then
        rm -rf file
        print_success "文件目录已删除"
    fi

    print_success "所有资源已完全清理"
}

# 查看状态
status() {
    check_docker

    if check_container_exists; then
        echo ""
        echo "容器状态:"
        docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""

        if check_container_running; then
            print_success "服务正在运行"
            echo ""
            echo "访问地址:"
            echo -e "  - Web UI: ${BLUE}http://localhost:8000/ui${NC}"
            echo -e "  - API:    ${BLUE}http://localhost:8000/api${NC}"
        else
            print_warning "服务已停止"
        fi
    else
        print_info "容器不存在"
    fi
}

# 主入口
main() {
    # 切换到脚本所在目录
    cd "$(dirname "$0")"

    case "${1:-deploy}" in
        deploy)
            deploy
            ;;
        start)
            check_docker
            check_docker_compose
            start_container
            check_service
            show_status
            ;;
        stop)
            check_docker
            check_docker_compose
            stop_service
            ;;
        restart)
            check_docker
            check_docker_compose
            restart_service
            ;;
        logs)
            check_docker
            show_logs
            ;;
        status)
            status
            ;;
        build)
            check_docker
            check_docker_compose
            build_image
            ;;
        clean)
            clean
            ;;
        clean-all)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
