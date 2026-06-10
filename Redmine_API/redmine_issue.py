from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError, AuthError, ValidationError
import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedmineHelper:
    def __init__(self, url, api_key):
        """
        初始化 Redmine 连接
        :param url: Redmine 服务器地址
        :param api_key: 用户的 API 密钥
        """
        self.redmine = Redmine(url, key=api_key, requests={'verify': False})  # verify=False 忽略SSL证书验证，根据需要修改
        logger.info(f"成功连接到 Redmine 服务器: {url}")

    def get_project_info(self, project_id):
        """
        获取项目信息:cite[6]
        :param project_id: 项目ID或标识符
        """
        try:
            project = self.redmine.project.get(project_id)
            logger.info(f"项目信息 - ID: {project.id}, 名称: {project.name}, 标识符: {project.identifier}")
            print(f"\n--- 项目信息 ---")
            print(f"项目名称: {project.name}")
            print(f"项目描述: {project.description}")
            print(f"项目主页: {project.homepage if hasattr(project, 'homepage') else 'N/A'}")
            print(f"创建时间: {project.created_on}")
            print(f"更新时间: {project.updated_on}")
            return project
        except ResourceNotFoundError:
            logger.error(f"未找到ID或标识符为 '{project_id}' 的项目")
        except Exception as e:
            logger.error(f"获取项目信息时发生错误: {e}")
        return None

    def create_issue(self, project_id, subject, description, tracker_id=None, priority_id=None, assigned_to_id=None, parent_issue_id=None, custom_fields=None):
        """
        创建问题（Issue）:cite[5]
        :param project_id: 项目ID
        :param subject: 问题主题
        :param description: 问题描述
        :param tracker_id: 跟踪标签ID（例如：1-缺陷，2-功能，3-支持）
        :param priority_id: 优先级ID（例如：4-低，5-普通，6-高，7-紧急）
        :param assigned_to_id: 指派给的用户ID
        :param parent_issue_id: 父任务ID（用于创建子任务）:cite[5]
        :param custom_fields: 自定义字段列表，例如 [{"id": 1, "value": "自定义值1"}]
        """
        try:
            issue = self.redmine.issue.new()
            issue.project_id = project_id
            issue.subject = subject
            issue.description = description
            if tracker_id:
                issue.tracker_id = tracker_id
            if priority_id:
                issue.priority_id = priority_id
            if assigned_to_id:
                issue.assigned_to_id = assigned_to_id
            if parent_issue_id:
                issue.parent_issue_id = parent_issue_id
            if custom_fields:
                issue.custom_fields = custom_fields

            issue.save()
            logger.info(f"成功创建问题: {issue.id} - {issue.subject}")
            print(f"\n--- 新问题创建成功 ---")
            print(f"问题ID: {issue.id}")
            print(f"问题链接: {self.redmine.url}/issues/{issue.id}")
            return issue
        except ValidationError as e:
            logger.error(f"创建问题验证失败: {e}")
        except Exception as e:
            logger.error(f"创建问题时发生错误: {e}")
        return None

    def add_issue_note(self, issue_id, notes):
        """
        为指定问题添加备注（注释）:cite[8]
        :param issue_id: 问题ID
        :param notes: 备注内容
        """
        try:
            issue = self.redmine.issue.get(issue_id)
            issue.notes = notes
            issue.save()
            logger.info(f"已为问题 #{issue_id} 添加备注")
            return True
        except ResourceNotFoundError:
            logger.error(f"未找到ID为 {issue_id} 的问题")
        except Exception as e:
            logger.error(f"添加备注时发生错误: {e}")
        return False

    def check_overdue_issues(self, project_id, days_threshold=1):
        """
        检查指定项目中即将到期（在days_threshold天内）或已过期的问题:cite[7]
        :param project_id: 项目ID
        :param days_threshold: 天数阈值，检查在此天内到期的问题
        """
        try:
            # 计算日期
            today = datetime.date.today()
            future_date = today + datetime.timedelta(days=days_threshold)

            # 构建过滤条件：获取指定项目中未关闭且到期日小于等于future_date的问题
            issues = self.redmine.issue.filter(
                project_id=project_id,
                status_id='*',  # 所有状态
                # 可以根据需要添加更多过滤条件，例如状态为开放
                due_date=f"<={future_date.isoformat()}"
            )

            overdue_issues = []
            upcoming_issues = []

            for issue in issues:
                if issue.due_date is None:
                    continue
                due_date = datetime.datetime.strptime(issue.due_date, '%Y-%m-%d').date()
                if due_date < today:
                    overdue_issues.append(issue)
                elif due_date <= future_date:
                    upcoming_issues.append(issue)

            # 打印结果
            print(f"\n--- 问题到期检查报告 (项目ID: {project_id}) ---")
            print(f"检查日期: {today}")
            print(f"阈值: {days_threshold} 天")
            print(f"已过期的问题数量: {len(overdue_issues)}")
            for issue in overdue_issues:
                print(f"  [已过期] #{issue.id} - {issue.subject} (到期日: {issue.due_date})")
            print(f"即将到期（{days_threshold}天内）的问题数量: {len(upcoming_issues)}")
            for issue in upcoming_issues:
                print(f"  [即将到期] #{issue.id} - {issue.subject} (到期日: {issue.due_date})")

            return overdue_issues, upcoming_issues

        except Exception as e:
            logger.error(f"检查过期问题时发生错误: {e}")
        return [], []


# 示例用法
if __name__ == '__main__':
    # 请替换成你的 Redmine 地址和 API 密钥
    REDMINE_URL = 'http://10.10.36.54:3000/'
    # 在你的Redmine账户页面（我的账户）生成API密钥:cite[4]
    API_KEY = 's0HA97J40FEUvRb5LDP6'

    # 初始化
    try:
        redmine_helper = RedmineHelper(REDMINE_URL, API_KEY)
    except AuthError:
        logger.error("认证失败，请检查URL和API密钥")
        exit(1)
    except Exception as e:
        logger.error(f"连接Redmine失败: {e}")
        exit(1)

    # 示例1: 获取项目信息:cite[6]
    PROJECT_IDENTIFIER_OR_ID = 'test'  # 可以是项目ID（数字）或标识符（字符串）
    project = redmine_helper.get_project_info(PROJECT_IDENTIFIER_OR_ID)

    if project:
        # 示例2: 创建一个新的问题（Bug）:cite[5]
        new_issue = redmine_helper.create_issue(
            project_id=project.id,
            subject='自动化脚本创建的Bug示例',
            description='这是一个由Python脚本自动创建的Bug描述。\n\n**重现步骤**:\n1. 第一步\n2. 第二步\n\n**预期结果**:\n应该这样\n\n**实际结果**:\n实际那样',
            tracker_id=1,  # 1 通常是 Bug，请根据你的Redmine设置调整
            priority_id=6,  # 6 通常是高优先级，请根据你的Redmine设置调整
            # assigned_to_id=123,  # 可以指定给某个用户
            # parent_issue_id=456,  # 可以指定父任务ID:cite[5]
            # custom_fields=[{'id': 1, 'value': '某个自定义字段值'}]  # 可选，设置自定义字段:cite[1]
        )

        # 示例3: 如果创建成功，为它添加一条备注:cite[8]
        if new_issue:
            redmine_helper.add_issue_note(new_issue.id, "这是一条由脚本自动添加的备注，用于测试。")

        # 示例4: 检查即将到期或已过期的问题:cite[7]
        redmine_helper.check_overdue_issues(project.id, days_threshold=3)