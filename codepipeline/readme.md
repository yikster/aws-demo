# What's this
This is for helping the operators that they want to automate some part of deployment between production AWS account and developement AWS account.

# Purpose
This code is simplify the connection between accounts, so operator can build deployment connection without any single console access in few minutes. Developers can build development environment using CodeStar. In minutes, CodeStar build repository (CodeCommit), build process(CodeBuild), and deployment(CodeDeploy). But all of them, exists in Development AWS Account. Development team needs deploy to the production environment. And before to deploy to the production, it is required some kind of approval of managers. It add this step into CodeStar's pipeline automatically.

# Development Life Cycle
Generally, development life cyle looks like below pictures. Many of optimzed DevOps teams using this kind of pipelines seemless.

# Architecture
First of all, we need to know what resources and what connection is built for this Development Life Cycle. Below picture show the full resources and connection on two account ( Development AWS Account and Production AWS Account)

# Requirements
Build for this resources we need below items.

# Ownership

# Developers

# Operators

# Codes

## CodePipeline on Development Account

## CodeDeploy and Autoscalinggroup on Production Account
