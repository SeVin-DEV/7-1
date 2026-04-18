import subprocess
 
 
 def initialize_bus(app, manifest):
     """
     Registers patch capabilities into system context.
     Used for LLM awareness only (not execution logic).
     """
     if not hasattr(app, "extra_instructions"):
         app.extra_instructions = []
 
     app.extra_instructions.append(
         f"PATCH_BUS_ACTIVE: Terminal Access Enabled | Modules: [{manifest}]"
     )
 
 
 def call(command):
     """
     Executes shell commands safely through controlled subprocess layer.
     """
 
     if not command or not isinstance(command, str):
         return "EXEC_ERROR: Invalid command input."
 
     try:
         result = subprocess.run(
             command,
             shell=True,
             text=True,
             capture_output=True,
             timeout=15
         )
 
         if result.returncode != 0:
             return f"EXEC_ERROR: {result.stderr.strip()}"
 
         return result.stdout.strip() or "Success (No Output)."
 
     except subprocess.TimeoutExpired:
         return "EXEC_ERROR: Command timed out."
 
     except Exception as e:
         return f"EXEC_ERROR: {str(e)}"import subprocess
 
 
 def initialize_bus(app, manifest):
     """
     Registers patch capabilities into system context.
     Used for LLM awareness only (not execution logic).
     """
     if not hasattr(app, "extra_instructions"):
         app.extra_instructions = []
 
     app.extra_instructions.append(
         f"PATCH_BUS_ACTIVE: Terminal Access Enabled | Modules: [{manifest}]"
     )
 
 
 def call(command):
     """
     Executes shell commands safely through controlled subprocess layer.
     """
 
     if not command or not isinstance(command, str):
         return "EXEC_ERROR: Invalid command input."
 
     try:
         result = subprocess.run(
             command,
             shell=True,
             text=True,
             capture_output=True,
             timeout=15
         )
 
         if result.returncode != 0:
             return f"EXEC_ERROR: {result.stderr.strip()}"
 
         return result.stdout.strip() or "Success (No Output)."
 
     except subprocess.TimeoutExpired:
         return "EXEC_ERROR: Command timed out."
 
     except Exception as e:
         return f"EXEC_ERROR: {str(e)}"
