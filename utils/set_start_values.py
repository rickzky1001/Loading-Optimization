import gurobipy as gp
def set_start_values(model:gp.Model, initial_values:dict):
    for var_name, values in initial_values.items():
        for idx, value in values.items():
            if isinstance(idx, tuple):
                idx_str = ",".join(map(str, idx))  # 将元组转换为逗号分隔的字符串
            else:
                idx_str = str(idx)
            var = model.getVarByName(f"{var_name}[{idx_str}]")
            if var is not None:
                var.Start = value
            else:
                raise ValueError(f"Variable '{var_name}[{idx_str}]' not found in the model.")