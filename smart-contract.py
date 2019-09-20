import datetime
import json

from stellar_base import Address
from stellar_base.builder import Builder

# NWC ISSUER ADDRESS
ISSUER = 'GDZJD363YP7P3TNYDK3ZD6GLXFMAI3GLVIH7CGFLNZWIZBQUCVE6PTU7'
REAL_SEED = '<ISSUER-SECRET>'
BURN_RATE = 0.20


def send_payment(address, amount):
    builder = Builder(secret=REAL_SEED, network='public')
    builder.add_text_memo("NWC transaction amount: {}".format(amount)).append_payment_op(
        destination=address, amount=amount, asset_code='NWC', asset_issuer=ISSUER)
    builder.sign()
    response = builder.submit()
    print(response)
    with open("transaction.log", "a+") as log:
        log.write("\n")
        log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        log.write("\n")
        log.write("=============================================")
        log.write("\n")
        log.write(json.dumps(response))
        log.write("\n")


def bounty_dispatcher(document, amount):
    """
    Dispatch amount specified to the destination address
    :param document: Desetination address
    :param amount: Amount of nwc to dispatch
    :return: response object
    """
    for line in document:
        builder = Builder(secret=REAL_SEED, network='public')
        builder.add_text_memo("NWC bounty reward amount: {}".format(amount)).append_payment_op(
            destination=line, amount=amount, asset_code='NWC', asset_issuer=ISSUER)
        builder.sign()
        response = builder.submit()
        print(response)
        with open("bounty.log", "a+") as log:
            log.write("\n")
            log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            log.write("\n")
            log.write("=============================================")
            log.write("\n")
            log.write(json.dumps(response))
            log.write("\n")
    return response


def send_payment_and_lock(address, amount, release, valid):
    """
    Send the payment to the specified address and lock it for the specified time period
    :param address: Destination address
    :param amount:  Amount of NWC to payout
    :param release: Start of token lock date
    :param valid:  End of token lock date
    :return: response object
    """
    timestamp_release = (release - datetime.datetime(1970, 1, 1)).total_seconds()
    timestamp_valid = (valid - datetime.datetime(1970, 1, 1)).total_seconds()
    builder = Builder(secret=REAL_SEED, network='public')
    builder.add_text_memo(
        "NWC transaction amount: {}; asset locked till: {}".format(amount, release)).append_payment_op(
        destination=address, amount=amount, asset_code='NWC', asset_issuer=ISSUER).add_time_bounds(
        {
            'minTime': timestamp_release,
            'maxTime': timestamp_valid})
    builder.sign()
    response = builder.submit()
    print(response)
    with open("transaction.log", "a+") as log:
        log.write("\n")
        log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        log.write("\n")
        log.write("unlocks: " + release.strftime("%Y-%m-%d %H:%M:%S"))
        log.write("\n")
        log.write("valid till: " + valid.strftime("%Y-%m-%d %H:%M:%S"))
        log.write("=============================================")
        log.write("\n")
        log.write(json.dumps(response))
        log.write("\n")
    return response


def burn_tokens(address):
    """
    Burn the recent payments to the address for the percent specified in the BURN_RATE constant
    :param address: address to burn the tokens on
    :return: response object
    """
    # get recent payments
    address_obj = Address(address=address)
    payments = address_obj.payments()
    asset_sum = 0
    for payment in payments:
        asset_sum += payment

    burn_sum = asset_sum * BURN_RATE

    # send the BURN % of tokens to the issuer ultimately taking them out of circulation
    builder = Builder(secret=REAL_SEED, network='public')
    builder.add_text_memo("NWC daily burn: {}".format(burn_sum)).append_payment_op(
        destination=ISSUER, amount=burn_sum, asset_code='NWC', asset_issuer=ISSUER)
    builder.sign()
    response = builder.submit()
    return response
