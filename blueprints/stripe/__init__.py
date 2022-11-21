# This file is licensed under CC0 Universal 1.0
from flask import Blueprint, Response, render_template, redirect, url_for, request, session, flash
import time
from pymongo.collection import ObjectId, ReturnDocument
import stripe
import stripe.error
import os
from fx import price_as
from multiprocessing import Process

# ensure you've loaded the .env file before this code runs
STRIPE_ORDER_EXPIRY = 60 * 20  # 20 minute checkout expiry
# DYNO is defined in Heroku so ignore that if you are using something like DigitalOcean
SERVER_ID = os.environ['DYNO'] if 'DYNO' in os.environ else os.environ['SERVER_ID']
stripe.api_key = os.environ['STRIPE_API_KEY']

stripe_bp = Blueprint('stripe', __name__, url_prefix='/stripe', template_folder='blueprints/stripe/templates')


def get_store_items():
    return [{
        '_id': '61d399ab875ac8db22440ffe',
        'name': 'Test Stripe',
        'item_id': 'debug-item',
        'description': 'A sample item to test stripe, dev API',
        # stripe takes in base units, so convert this later
        'price': 20.00,
        'cost': 0,
        'max_quantity': 1,
        'options': [],
        'payment_methods': ['credit_card'],
        'visible': True,
        'images': [
            'https://raw.githubusercontent.com/elibroftw/music-caster/master/resources/SC-Main.jpg'
        ],
        'image-files': {}
    }]


@stripe_bp.get('/checkout-example/')
def stripe_checkout_example():
    if 'cancelled' in request.args:
        flash('payment cancelled or failed', 'error')
    return render_template('store.html', store_items=get_store_items())


@stripe_bp.post('/add-to-cart/')
def stripe_add_to_cart():
    return redirect(url_for('stripe_checkout_example'))


@stripe_bp.route('/checkout/')
def stripe_checkout():
    # here you would add an item to your database as well as which server received the checkout.
    # since this is an example, I will store the order in a cookie
    host_url = request.host_url
    cart = session.get('cart', [])
    if cart:
        order = order = {
            # DYNO is for Heroku
            'server': SERVER_ID,
            'cart': cart,
            'payment_confirmed': False,
            'order_processed': False,
            'expired': False,
            'timestamp': time.time(),
            # 'payment_method': 'credit-card',
            # 'shipping_info': checkout_info,
            'total_usd': sum((item['price'] for item in cart)),
            'currency': 'USD',
        }
        order_id = order['_id'] = ObjectId()
        try:
            # https://stripe.com/docs/api/checkout/sessions/create
            checkout_sess = stripe.checkout.Session.create(
                # host_url ends with /
                # success_url ending should have a secret to show a notification
                success_url=f'{host_url}stripe/order/{order_id}/', # {{CHECKOUT_SESSION_ID}}
                cancel_url=f'{host_url}stripe/checkout-example/?cancelled={order_id}',
                line_items=[{'price_data': {
                                'currency': order['currency'],
                                'product_data': { 'name': item['name'] },
                                'unit_amount': int(price_as(item['price'], order['currency']) * 100) # in cents
                                },
                             'quantity': item['quantity']}
                            for item in order['cart']],
                mode='payment',
                # use this if you collect the email beforehand
                # customer_email=order['email'],
                expires_at=int(time.time()) + STRIPE_ORDER_EXPIRY)
            order.update({'stripe_session_id': checkout_sess['id'], 'stripe_checkout_url': checkout_sess['url']})
            if 'orders' not in session:
                session['orders'] = {}
            session['orders'][order_id] = order
            return redirect(checkout_sess['url'])
        except Exception as e:
            # send yourself a notification via Email, Telegram bot, Matrix bot, Discord webhook
            flash('internal error, could not process order', 'error')
            # in template, use {% with messages = get_flashed_messages(True) %}...
    return redirect(url_for('stripe_checkout_example'))


@stripe_bp.get('/order/<order_id>/<session_id>')
def stripe_order_completed(order_id, session_id=''):
    # do not assume that this endpoint can only be accessed by users who have paid
    # the session cookie is not encrypted only signed (tamper-proof, not readable-proof)

    # order := Db.get_order(order_id)
    # payment_confirmed = order['payment_confirmed']
    payment_confirmed = False
    if not payment_confirmed:
        # in my example, we check the payment status here
        # if you are scaling, use the webhook alternative
        try:
            checkout_sess = stripe.checkout.Session.retrieve(session_id)
            if checkout_sess['payment_status'] == 'paid':
                # Db.update_order(...)
                flash('payment successful')
        except Exception as e:
            # failed for unknown reason, tell user to do something else
            pass
    return render_template('order.html', order_id=order_id)


@stripe_bp.post('/webhook')
def stripe_checkout_webhook():
    # https://stripe.com/docs/api/events/types#event_types-checkout.session.completed
    # https://stripe.com/docs/webhooks/test
    # https://github.com/stripe-samples/checkout-one-time-payments/blob/main/server/python/server.py#L94
    # https://stripe.com/docs/webhooks/go-live
    # Preferably use this to avoid calling stripe API to check the payment status
    # in your implementation, you would update the order in your database
    return True


def stripe_cleanup_startup():
    # it's possible that during server maintainance a client paid for an order
    #  and Stripe's post request to the webhook failed to get through

    # outline
    # orders_to_check = Db.orders.find({'payment_method': 'credit-card', 'payment_confirmed': False,
                                   #    'expired': False, 'server': SERVER_ID})
    # expired_orders = []
    # for order in orders_to_check:
    # try:
    #     checkout_sess = stripe.checkout.Session.retrieve(checkout_id)
    #     if checkout_sess['payment_status'] == 'paid':
    #         Db.orders.find_one_and_update({'_id': order['_id']}, {'$set': {'payment_confirmed': True}})
    #     elif checkout_sess['status'] == 'expired':
    #         expired_orders.append(order)
    #     # quick exit for fast restarts
    #     if not os.path.exists(run_file):
    #         return
    #     time.sleep(0.5)
    # except (stripe.error.RateLimitError, stripe.error.APIConnectionError):
    #     # probably a rate limit (though the exception type might not be RateLimit)
    #     time.sleep(1)
    # except Exception as e:
    #     send error notification
    #     manually check if expired
    # time.sleep(60)
    pass
