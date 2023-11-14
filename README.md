# dining-concierge-chatbot

In this assignment, we will be building a Dining Concierge chatbot using Natural
Language Processing (NLP) and microservices. The chatbot will recommend
restaurants based on user preferences gathered through conversation.

## Chat flow

> Chatbot URL: https://vt2182-a1-s3.s3.amazonaws.com/chat.html

**Chatbot Concierge**

*Bot:* Hi there, I'm your personal Concierge. 

*User:* Hi

*Bot:* Hi there, how can I help?

*User:* I need some restaurant suggestions.

*Bot:* Great. I can help you with that. What city or city area are you looking to dine in?

*User:* Manhattan

*Bot:* Got it, Manhattan. What cuisine would you like to try?

*User:* Indian

*Bot:* Ok, how many people are in your party?

*User:* Eight

*Bot:* A few more to go. What date?

*User:* Tomorrow

*Bot:* What time?

*User:* 8 PM

*Bot:* Great. Lastly, I need your email so I can send you my findings.

*User:* vt2182@nyu.edu

*Bot:* Thanks, I have placed your reservation.

*User:* Thank you

*Bot:* You're welcome!

## Architecture

![Architecture](./dining-concierge-chatbot.drawio.png)

## Screenshots

Checkout the [screenshots.md](./screenshots.md) for a detailed walkthrough of
the project.

## AWS Services

- [Amazon S3](https://aws.amazon.com/s3/)
- [Amazon API Gateway](https://aws.amazon.com/api-gateway/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Amazon Lex](https://aws.amazon.com/lex/)
- [Amazon SQS](https://aws.amazon.com/sqs/)
- [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)
- [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/)
- [Amazon Cloud9](https://aws.amazon.com/cloud9/)
- [Amazon SES](https://aws.amazon.com/ses/)

## External Services

- [Yelp Fusion API](https://www.yelp.com/fusion)
- [Colab](https://colab.research.google.com/)
