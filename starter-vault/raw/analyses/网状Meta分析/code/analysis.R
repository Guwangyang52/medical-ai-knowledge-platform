# 网状Meta分析（NMA）— BUGSnet包实现贝叶斯NMA
# 参考：向虹等(2022). 中国循证医学杂志

# ============================================================
# 0. 安装与加载包
# ============================================================
# 首次使用需安装BUGSnet（需Rtools和JAGS）
# install.packages(c("remotes", "knitr"))
# remotes::install_github("audrey-b/BUGSnet@v1.1.0")
# install.packages(c("readxl", "dplyr", "tidyr", "ggplot2", "gridExtra"))

library(dplyr)
library(tidyr)
library(BUGSnet)
library(ggplot2)
library(gridExtra)

# ============================================================
# 1. 数据导入与整理
# ============================================================
data_total <- read.csv("data/nma_sample_data.csv", check.names = FALSE, fileEncoding = "UTF-8-BOM")

# 提取不同结局指标
data_remission <- data_total[, c(1:4)]  # 主要疗效指标：缓解
data_relapse <- data_total[, c(1:3, 5)]  # 次要疗效指标：复发
data_withdrawal <- data_total[, c(1:3, 6)]  # 安全性指标：退出
data_dose <- data_total[, c(1:3, 7:8)]  # 安全性指标：类固醇剂量

# 数据清洗与重命名
data_remission <- data_remission %>%
  rename(sampleSize=Number.of.patients, events=Number.of.remissions)

data_relapse <- data_relapse %>%
  drop_na() %>%
  rename(sampleSize=Number.of.patients, events=Number.of.relapses)

data_withdrawal <- data_withdrawal %>%
  drop_na() %>%
  rename(sampleSize=Number.of.patients, events=Number.of.adverse.event.related.withdrawals)

data_dose <- data_dose %>%
  drop_na() %>%
  rename(sampleSize=Number.of.patients, mean=Cumulative.dose.of.steroid_Mean,
         SD=Cumulative.dose.of.steroid_SD)

# ============================================================
# 2. BUGSnet数据预处理
# ============================================================
data_remission <- data.prep(arm.data=data_remission,
                            varname.t="Treatment", varname.s="Study")

data_dose <- data.prep(arm.data=data_dose,
                       varname.t="Treatment", varname.s="Study")

# ============================================================
# 3. 证据网络图
# ============================================================
par(mfrow=c(1,2))
net.plot(data_remission, node.colour="#CB3127", edge.colour="dark grey")
net.plot(data_dose, node.colour="blue")

# ============================================================
# 4. 模型设置（固定效应 + 随机效应）
# ============================================================
# 缓解率—固定效应
fixed_remission <- nma.model(data=data_remission, outcome="events",
    N="sampleSize", reference="Steroid alone",
    family="binomial", link="logit", effects="fixed")

# 剂量—固定效应
fixed_dose <- nma.model(data=data_dose, outcome="mean",
    N="sampleSize", sd="SD", reference="Steroid alone",
    family="normal", link="identity", effects="fixed")

# 缓解率—随机效应
random_remission <- nma.model(data=data_remission, outcome="events",
    N="sampleSize", reference="Steroid alone",
    family="binomial", link="logit", effects="random")

# 剂量—随机效应
random_dose <- nma.model(data=data_dose, outcome="mean",
    N="sampleSize", sd="SD", reference="Steroid alone",
    family="normal", link="identity", effects="random")

# ============================================================
# 5. 贝叶斯MCMC计算
# ============================================================
set.seed(20222022)

fixed_res_remission <- nma.run(fixed_remission, n.adapt=1000, n.burnin=1000, n.iter=10000)
fixed_res_dose <- nma.run(fixed_dose, n.adapt=1000, n.burnin=1000, n.iter=10000)

random_res_remission <- nma.run(random_remission, n.adapt=1000, n.burnin=1000, n.iter=10000)
random_res_dose <- nma.run(random_dose, n.adapt=1000, n.burnin=1000, n.iter=10000)

# ============================================================
# 6. 模型评估（DIC比较）
# ============================================================
par(mfrow=c(2,2))
nma.fit(fixed_res_remission)
nma.fit(fixed_res_dose)
nma.fit(random_res_remission)
nma.fit(random_res_dose)

# ============================================================
# 7. 排序结果
# ============================================================
sucra_remission <- nma.rank(random_res_remission, largerbetter=TRUE)
sucra_dose <- nma.rank(fixed_res_dose, largerbetter=FALSE)

# 自定义颜色
z <- scale_colour_manual(values=c(
  AZA="#FF6600", MMF="#FF0088", "Steroid alone"="#00FF00",
  CP_P="#007700", Cyclosporine="#6633CC",
  "DCP_C(6M)"="#00CCFF", "DCP_C(12M)"="#FFFF00",
  Rituximab="#AA0000"))

# SUCRA图
s1 <- sucra_remission$sucraplot + z
s4 <- sucra_dose$sucraplot + z

# Rankogram图
r1 <- sucra_remission$rankogram +
  theme(axis.text.x=element_text(angle=30, hjust=1, vjust=1))
r4 <- sucra_dose$rankogram +
  theme(axis.text.x=element_text(angle=30, hjust=1, vjust=1))

grid.arrange(s1, s4, r1, r4, ncol=2)

# ============================================================
# 8. League table热图
# ============================================================
league_remission <- nma.league(random_res_remission,
    central.tdcy="median", order=sucra_remission$order,
    log.scale=TRUE, low.colour="springgreen4",
    mid.colour="white", high.colour="red", digits=2)

league_dose <- nma.league(fixed_res_dose,
    central.tdcy="median", order=sucra_dose$order,
    log.scale=TRUE, low.colour="springgreen4",
    mid.colour="white", high.colour="red", digits=2)

grid.arrange(league_remission$heatplot, league_dose$heatplot, ncol=1)

# 输出表格
league_remission$table
league_remission$longtable

# ============================================================
# 9. 森林图（vs 参照组）
# ============================================================
f1 <- nma.forest(random_res_remission, central.tdcy="median",
                  log.scale=TRUE, comparator="Steroid alone")
f4 <- nma.forest(random_res_remission, central.tdcy="median",
                  log.scale=TRUE, comparator="Steroid alone")
grid.arrange(f1, f4, ncol=2)
