from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TPMAutoCheck:
    def __init__(self):
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """设置Edge浏览器驱动"""
        try:
            # Edge浏览器选项
            edge_options = Options()
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            edge_options.add_argument('--start-maximized')
            
            # 自动查找Edge驱动路径
            service = Service()
            self.driver = webdriver.Edge(service=service, options=edge_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("Edge浏览器驱动设置完成")
            return True
        except Exception as e:
            logger.error(f"设置浏览器驱动失败: {e}")
            return False
    
    def login(self):
        """登录系统"""
        try:
            logger.info("正在访问登录页面...")
            self.driver.get("http://192.168.71.187:8181/webroot/decision/login")
            
            # 等待页面加载并输入账号密码
            logger.info("正在输入登录信息...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
            username_input.clear()
            username_input.send_keys("alex_xu")
            password_input.clear()
            password_input.send_keys("qwe1230.asd")
            
            # 点击登录按钮
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='button']")
            login_button.click()
            logger.info("登录信息已提交")
            
            # 等待登录成功
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return False
    
    def navigate_to_etpm(self):
        """导航到ETPM模块"""
        try:
            logger.info("正在导航到TPM系统...")
            
            # 点击TPM设备管理系统
            tpm_menu = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".bi-label.bi-text"))
            )
            tpm_menu.click()
            time.sleep(2)
            
            # 点击ETPM-手机APP模拟登录
            etpm_item = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".bi-label.dec-frame-text.bi-text"))
            )
            etpm_item.click()
            logger.info("已进入ETPM模块")
            
            # 等待右侧界面加载
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"导航到ETPM失败: {e}")
            return False
    
    def etpm_login(self):
        """ETPM系统登录"""
        try:
            logger.info("正在登录ETPM系统...")
            
            # 切换到iframe（如果有）
            frames = self.driver.find_elements(By.TAG_NAME, "iframe")
            if frames:
                self.driver.switch_to.frame(frames[0])
                logger.info("已切换到iframe")
            
            # 输入ETPM账号
            username_inputs = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".uni-input-placeholder.placeClass"))
            )
            
            if len(username_inputs) >= 2:
                username_inputs[0].clear()
                username_inputs[0].send_keys("H033398")
                logger.info("已输入ETPM账号")
                
                # 输入ETPM密码
                username_inputs[1].clear()
                username_inputs[1].send_keys("H033398")
                logger.info("已输入ETPM密码")
            else:
                # 如果找不到两个输入框，尝试分别查找
                etpm_username = self.driver.find_element(By.CSS_SELECTOR, ".uni-input-placeholder.placeClass")
                etpm_username.clear()
                etpm_username.send_keys("H033398")
                logger.info("已输入ETPM账号")
                
                # 可能需要等待一下再找第二个输入框
                time.sleep(1)
                etpm_password = self.driver.find_elements(By.CSS_SELECTOR, ".uni-input-placeholder.placeClass")[1]
                etpm_password.clear()
                etpm_password.send_keys("H033398")
                logger.info("已输入ETPM密码")
            
            # 点击登录按钮
            login_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-btn"))
            )
            login_btn.click()
            logger.info("ETPM登录按钮已点击")
            
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"ETPM登录失败: {e}")
            return False
    
    def select_factory(self, factory_name):
        """选择工厂"""
        try:
            logger.info(f"正在选择工厂: {factory_name}")
            
            # 点击工厂选择框
            factory_select = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".uni-view.input-box.flex.align-center"))
            )
            factory_select.click()
            time.sleep(2)
            
            # 选择指定的工厂
            factory_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{factory_name}')]"))
            )
            factory_option.click()
            logger.info(f"已选择工厂: {factory_name}")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"选择工厂失败: {e}")
            return False
    
    def process_check_items(self):
        """处理点检项目"""
        try:
            logger.info("正在处理点检项目...")
            
            # 查找所有需要点检的项目
            check_items = self.driver.find_elements(By.CSS_SELECTOR, "div.uni-scroll-view-refresher")
            logger.info(f"找到 {len(check_items)} 个点检项目")
            
            for i, item in enumerate(check_items):
                try:
                    logger.info(f"正在处理第 {i+1} 个项目")
                    
                    # 点击进入项目详情
                    item.click()
                    time.sleep(3)
                    
                    # 处理测试类项目
                    if self.process_test_items():
                        # 返回上一级
                        back_button = self.driver.find_elements(By.CSS_SELECTOR, ".uni-view.save")
                        if back_button:
                            back_button[0].click()
                        else:
                            # 如果没有找到返回按钮，尝试点击其他地方返回
                            self.driver.back()
                        
                        time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"处理第 {i+1} 个项目时出错: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"处理点检项目失败: {e}")
            return False
    
    def process_test_items(self):
        """处理测试类项目"""
        try:
            # 查找所有测试类项目
            test_items = self.driver.find_elements(By.CSS_SELECTOR, ".uni-view.content-card-box.flex.flex-direction")
            logger.info(f"找到 {len(test_items)} 个测试类项目")
            
            for i, test_item in enumerate(test_items):
                try:
                    logger.info(f"正在处理第 {i+1} 个测试类项目")
                    
                    # 点击测试类项目展开
                    test_item.click()
                    time.sleep(2)
                    
                    # 查找并点击OK按钮
                    ok_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".uni-radio-input.uni-radio-input-checked")
                    for button in ok_buttons:
                        if button.text == "OK" or button.get_attribute("value") == "OK":
                            button.click()
                            logger.info("已点击OK按钮")
                            break
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"处理测试类项目 {i+1} 时出错: {e}")
                    continue
            
            # 点击通过按钮
            pass_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".uni-view.save"))
            )
            pass_button.click()
            logger.info("已点击通过按钮")
            
            time.sleep(3)
            return True
            
        except Exception as e:
            logger.error(f"处理测试类项目失败: {e}")
            return False
    
    def run_auto_check(self):
        """运行自动点检"""
        try:
            logger.info("开始自动点检流程...")
            
            # 设置浏览器
            if not self.setup_driver():
                return False
            
            # 登录主系统
            if not self.login():
                return False
            
            # 导航到ETPM
            if not self.navigate_to_etpm():
                return False
            
            # ETPM登录
            if not self.etpm_login():
                return False
            
            # 处理各个工厂
            factories = ["三厂", "四厂", "二厂pad"]
            
            for factory in factories:
                logger.info(f"开始处理 {factory}")
                
                # 选择工厂
                if not self.select_factory(factory):
                    logger.warning(f"选择 {factory} 失败，跳过")
                    continue
                
                # 处理点检项目
                if not self.process_check_items():
                    logger.warning(f"处理 {factory} 的点检项目失败")
                    continue
                
                logger.info(f"完成处理 {factory}")
                time.sleep(2)
            
            logger.info("所有工厂点检完成！")
            return True
            
        except Exception as e:
            logger.error(f"自动点检流程执行失败: {e}")
            return False
        finally:
            if self.driver:
                logger.info("关闭浏览器...")
                self.driver.quit()

def main():
    """主函数"""
    auto_check = TPMAutoCheck()
    success = auto_check.run_auto_check()
    
    if success:
        logger.info("自动点检程序执行成功！")
    else:
        logger.error("自动点检程序执行失败！")

if __name__ == "__main__":
    main()