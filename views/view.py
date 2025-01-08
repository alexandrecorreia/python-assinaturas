import __init__
from models.database import engine
from models.model import Subscription, Payments
from sqlmodel import Session, select
from datetime import date, datetime

class SubscriptionService:
    def __init__(self, engine):
        self.engine = engine

    def create(self, subscription: Subscription):
        with Session(self.engine) as session:
            session.add(subscription)
            session.commit()
            return subscription

    def delete(self, id):
        with Session(self.engine) as session:
            query = select(Subscription).where(Subscription.id == id)
            result = session.exec(query).one()
            session.delete(result)
            session.commit()

    def list_all(self):
        with Session(self.engine) as session:
            query = select(Subscription)
            results = session.exec(query).all()
        return results            
    
    def _has_pay(self, results):
        for result in results:
            if result.date.month == date.today().month:
                return True
        
        return False

    def pay(self, subscription: Subscription):
        with Session(self.engine) as session:
            query = select(Payments).join(Subscription).where(Subscription.empresa == subscription.empresa)
            results = session.exec(query).all()
            
            if self._has_pay(results):
                question = input('Essa conta já foi paga este mês, deseja pagar novamente ? Y ou N')

                if not question.upper() == 'Y':
                    return
                
            pay = Payments(subscription_id=subscription.id, date=date.today())
            session.add(pay)
            session.commit()

    def total_value(self):
        with Session(self.engine) as session:
            query = select(Subscription)
            results = session.exec(query).all()

        total = 0

        for result in results:
            total += result.valor

        return float(total)

    def _get_last_12_months_native(self):
        today =  datetime.now()
        year = today.year
        month = today.month

        last_12_month = []

        for _ in range(12):
            last_12_month.append((month,year))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        
        return last_12_month[::-1]

    def _get_values_for_months(self, last_12_months):
        with Session(self.engine) as session:
            query = select(Payments)
            results = session.exec(query).all()

            value_for_months = []

            for i in last_12_months:
                value = 0
                for result in results:
                    if result.date.month == i[0] and result.date.year == i[1]:
                        value += float(result.subscription.valor)

                value_for_months.append(value)

            return value_for_months    

    def gen_chart(self):
        last_12_months = self._get_last_12_months_native()
        values_for_months = self._get_values_for_months(last_12_months)
        last_12_months = list(map(lambda x : x[0], self._get_last_12_months_native()))

        import matplotlib.pyplot as plt
        
        plt.plot( last_12_months, values_for_months )
        plt.show()


#if __name__ == '__main__':
    
    #ss = SubscriptionService(engine)

    #subscription = Subscription(empresa='Neflix',site='netflix.com.br',data_assinatura=date.today(), valor=25)
    #subscription = Subscription(empresa='Amazom',site='amazon.com.br',data_assinatura=date.today(), valor=12)
    #ss.pay(subscription)

    # assinaturas = ss.list_all()
    # for i,s in enumerate(assinaturas):
    #     print( f"[{i}] : {s.empresa}")

    # x = int(input("Escolha os itens acima : "))
    # ss.pay(assinaturas[x])

    #print(ss.total_value())
    #print(ss.gen_chart())