# Stripe Sessions Checkout Example

This is an example of how to use the Stripe API to accept credit card payment.
If you are using a frontend framework like React, modify the routes to return JSON instead of HTML.

If I have the time, I will use [CockroachDB](https://www.cockroachlabs.com/blog/migrate-heroku-postgres-cockroachdb-serverless/#step-2-create-a-cockroachdb-cloud-account) as a database to give a full code example.

A production demo can be seen on [lenerva.com/store](https://lenerva.com/store). This is my business website and is not open source because I had to code everything myself.

It uses MongoDB but I don't want to access it from my personal website.

## Stripe Cleanup Service

Suppose you needed to restart your servers because there was an update and just before you did that a user created an order and paid on Stripe. Stripe tries to reach your webhook but fails! Create a service that will run on server startup and check all leftover stripe payments and expire them if they are old or confirm the payment if the webhook missed it. This assumes that your order processing code is seperate from your payment confirmation code. This seperation helps you avoid duplicate order processing.

## Order Processing Guide

To process orders, you can either rely on a message queue with which orders to process and skip a database query, or you can query the database for all orders that are unfulfilled and go through it like that. I took the path of relying on the database since there's no good tutorials on how to use RabbitMQ effectively.

A question to keep at the back of your mind is whether all orders should be in the same collection or be grouped into pending, expired, and completed.
