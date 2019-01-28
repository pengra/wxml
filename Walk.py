from rakan import PyRakan as BaseRakan


class IowaModel(BaseRakan):


   def walk(self, num_steps: int):
        # walk for determined number of steps 
        for i in range(num_steps):
            self.step()
