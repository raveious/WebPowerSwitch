import click
from WebPowerSwitch import WebPowerSwitch

def _action(args):
    power = WebPowerSwitch(args.get('hostname'), args.get('port'),
                           args.get('username'), args.get('password'))

    action = args.get('action')
    outlet = power.outlet[args.get('outlet')]

    if action is 'on':
        outlet.on()
    elif action is 'off':
        outlet.off()
    elif action is 'cycle':
        outlet.cycle(args.get('delay'))
    elif action is 'status':
        print('"{}" is currently {}'.format(outlet.name, 'ON' if outlet.status() else 'OFF'))


@click.group()
@click.option('-h', '--hostname', default='192.168.0.100', help='IP or hostname of the Web Power Switch')
@click.option('-o', '--port', default=80, help='Port the web interface can be found on')
@click.option('-u', '--username', default='admin', help='Username to control the web power switch as')
# @click.password_option('-p', '--password', default='1234', help='Password for user login')
@click.option('-p', '--password', default='1234', help='Password for user login')
@click.pass_obj
def cli(clx, hostname, port, username, password):
    ctx['hostname'] = hostname
    ctx['port'] = port
    ctx['username'] = username
    ctx['password'] = password

@cli.command()
@click.argument('outlet', type=int)
@click.pass_obj
def on(ctx, outlet):
    ctx['action'] = 'on'
    ctx['outlet'] = outlet
    _action(ctx)

@cli.command()
@click.argument('outlet', type=int)
@click.pass_obj
def off(ctx, outlet):
    ctx['action'] = 'off'
    ctx['outlet'] = outlet
    _action(ctx)

@cli.command()
@click.argument('outlet', type=int)
@click.option('-d', '--delay', default=None, type=int, help='Durration of power cycle')
@click.pass_obj
def cycle(ctx, outlet, delay):
    ctx['action'] = 'cycle'
    ctx['outlet'] = outlet
    ctx['delay'] = delay    
    _action(ctx)

@cli.command()
@click.argument('outlet', type=int)
@click.pass_obj
def status(ctx, outlet):
    ctx['action'] = 'status'
    ctx['outlet'] = outlet
    _action(ctx)

if __name__ == '__main__':
    ctx = {}
    cli(obj=ctx)