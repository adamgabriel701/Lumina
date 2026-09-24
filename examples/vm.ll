; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [37 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"array_lit" = alloca [5 x i64]
  %"arr_el_0" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 0
  store i64 16, i64* %"arr_el_0"
  %"arr_el_1" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 1
  store i64 42, i64* %"arr_el_1"
  %"arr_el_2" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 2
  store i64 32, i64* %"arr_el_2"
  %"arr_el_3" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 3
  store i64 0, i64* %"arr_el_3"
  %"arr_el_4" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 4
  store i64 255, i64* %"arr_el_4"
  %"bytecode" = alloca i64*
  %"ptr_cast" = bitcast [5 x i64]* %"array_lit" to i64*
  store i64* %"ptr_cast", i64** %"bytecode"
  %"pc" = alloca i64
  store i64 0, i64* %"pc"
  %"reg0" = alloca i64
  store i64 0, i64* %"reg0"
  br label %"while_cond"
while_cond:
  br i1 1, label %"while_body", label %"while_end"
while_body:
  %"bytecode_load" = load i64*, i64** %"bytecode"
  %"pc_load" = load i64, i64* %"pc"
  %".20" = getelementptr i64, i64* %"bytecode_load", i64 %"pc_load"
  %"ptr_idx_load" = load i64, i64* %".20"
  %"opcode" = alloca i64
  store i64 %"ptr_idx_load", i64* %"opcode"
  %"opcode_load" = load i64, i64* %"opcode"
  %"icmp" = icmp eq i64 %"opcode_load", 16
  br i1 %"icmp", label %"if_then", label %"if_else"
while_end:
  %"ret_trunc.2" = trunc i64 0 to i32
  ret i32 %"ret_trunc.2"
if_then:
  %"bytecode_load.1" = load i64*, i64** %"bytecode"
  %"pc_load.1" = load i64, i64* %"pc"
  %"add" = add i64 %"pc_load.1", 1
  %".23" = getelementptr i64, i64* %"bytecode_load.1", i64 %"add"
  %"ptr_idx_load.1" = load i64, i64* %".23"
  store i64 %"ptr_idx_load.1", i64* %"reg0"
  %"pc_load.2" = load i64, i64* %"pc"
  %"add.1" = add i64 %"pc_load.2", 2
  store i64 %"add.1", i64* %"pc"
  br label %"while_cond"
if_else:
  %"opcode_load.1" = load i64, i64* %"opcode"
  %"icmp.1" = icmp eq i64 %"opcode_load.1", 32
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_end:
  unreachable
if_then.1:
  %".28" = bitcast [6 x i8]* @"str_3" to i8*
  %".29" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".29", i8* %".28")
  %"reg0_load" = load i64, i64* %"reg0"
  %".30" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".31", i64 %"reg0_load")
  %".32" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %"pc_load.3" = load i64, i64* %"pc"
  %"add.2" = add i64 %"pc_load.3", 2
  store i64 %"add.2", i64* %"pc"
  br label %"while_cond"
if_else.1:
  %"opcode_load.2" = load i64, i64* %"opcode"
  %"icmp.2" = icmp eq i64 %"opcode_load.2", 255
  br i1 %"icmp.2", label %"if_then.2", label %"if_else.2"
if_end.1:
  unreachable
if_then.2:
  %".36" = bitcast [12 x i8]* @"str_8" to i8*
  %".37" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".37", i8* %".36")
  %".38" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".38")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_else.2:
  %".40" = bitcast [21 x i8]* @"str_11" to i8*
  %".41" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".41", i8* %".40")
  %"opcode_load.3" = load i64, i64* %"opcode"
  %".42" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".42")
  %".43" = bitcast [4 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".43", i64 %"opcode_load.3")
  %".44" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".44")
  %"ret_trunc.1" = trunc i64 1 to i32
  ret i32 %"ret_trunc.1"
if_end.2:
  unreachable
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [37 x i8] c"Iniciando M\c3\a1quina Virtual Lumina...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [6 x i8] c"Reg0:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [12 x i8] c"CPU Halted.\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c"\0a\00"
@"str_11" = constant [21 x i8] c"Opcode desconhecido:\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c" \00"
@"str_14" = constant [4 x i8] c"%ld\00"
@"str_15" = constant [2 x i8] c"\0a\00"