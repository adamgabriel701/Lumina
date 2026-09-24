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
@"g_pc" = internal global i64 512
define void @"cls"()
{
cls_entry:
  br label %"cls_body"
cls_body:
  %"mul" = mul i64 64, 32
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"mul"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"mul.1" = mul i64 64, 32
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 %"mul.1")
  %"i_load" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i8, i8* %"alloc_bytes_call", i64 %"i_load"
  %"elem_trunc" = trunc i64 32 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  ret void
}

define void @"draw_screen"()
{
draw_screen_entry:
  br label %"draw_screen_body"
draw_screen_body:
  %"y" = alloca i64
  store i64 0, i64* %"y"
  br label %"while_cond"
while_cond:
  %"y_load" = load i64, i64* %"y"
  %"icmp" = icmp slt i64 %"y_load", 32
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"x" = alloca i64
  store i64 0, i64* %"x"
  %".7" = bitcast [1 x i8]* @"str_0" to i8*
  %"row" = alloca i8*
  store i8* %".7", i8** %"row"
  br label %"while_cond.1"
while_end:
  ret void
while_cond.1:
  %"x_load" = load i64, i64* %"x"
  %"icmp.1" = icmp slt i64 %"x_load", 64
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"mul" = mul i64 64, 32
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 %"mul")
  %"y_load.1" = load i64, i64* %"y"
  %"mul.1" = mul i64 %"y_load.1", 64
  %"x_load.1" = load i64, i64* %"x"
  %"add" = add i64 %"mul.1", %"x_load.1"
  %".11" = getelementptr i8, i8* %"alloc_bytes_call", i64 %"add"
  %"ptr_idx_load" = load i8, i8* %".11"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"pixel" = alloca i64
  store i64 %"idx_sext", i64* %"pixel"
  %"pixel_load" = load i64, i64* %"pixel"
  %"icmp.2" = icmp eq i64 %"pixel_load", 35
  br i1 %"icmp.2", label %"if_then", label %"if_else"
while_end.1:
  %"row_load.2" = load i8*, i8** %"row"
  %".22" = bitcast [3 x i8]* @"str_3" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %"row_load.2")
  %".23" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %"y_load.2" = load i64, i64* %"y"
  %"add.2" = add i64 %"y_load.2", 1
  store i64 %"add.2", i64* %"y"
  br label %"while_cond"
if_then:
  %"row_load" = load i8*, i8** %"row"
  %".14" = bitcast [2 x i8]* @"str_1" to i8*
  %"sconcat_len1" = call i64 @"strlen"(i8* %"row_load")
  %"sconcat_len2" = call i64 @"strlen"(i8* %".14")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"row_load")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %".14")
  store i8* %"sconcat_buf", i8** %"row"
  br label %"if_end"
if_else:
  %"row_load.1" = load i8*, i8** %"row"
  %".17" = bitcast [2 x i8]* @"str_2" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"row_load.1")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".17")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"row_load.1")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".17")
  store i8* %"sconcat_buf.1", i8** %"row"
  br label %"if_end"
if_end:
  %"x_load.2" = load i64, i64* %"x"
  %"add.1" = add i64 %"x_load.2", 1
  store i64 %"add.1", i64* %"x"
  br label %"while_cond.1"
}

define void @"load_game"()
{
load_game_entry:
  br label %"load_game_body"
load_game_body:
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr" = getelementptr i8, i8* %"alloc_bytes_call", i64 512
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"alloc_bytes_call.1" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_bytes_call.1", i64 513
  %"elem_trunc.1" = trunc i64 224 to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"alloc_bytes_call.2" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr.2" = getelementptr i8, i8* %"alloc_bytes_call.2", i64 514
  %"elem_trunc.2" = trunc i64 96 to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"alloc_bytes_call.3" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr.3" = getelementptr i8, i8* %"alloc_bytes_call.3", i64 515
  %"elem_trunc.3" = trunc i64 10 to i8
  store i8 %"elem_trunc.3", i8* %"idx_ptr.3"
  %"alloc_bytes_call.4" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr.4" = getelementptr i8, i8* %"alloc_bytes_call.4", i64 516
  %"elem_trunc.4" = trunc i64 112 to i8
  store i8 %"elem_trunc.4", i8* %"idx_ptr.4"
  %"alloc_bytes_call.5" = call i8* @"GC_malloc"(i64 4096)
  %"idx_ptr.5" = getelementptr i8, i8* %"alloc_bytes_call.5", i64 517
  %"elem_trunc.5" = trunc i64 5 to i8
  store i8 %"elem_trunc.5", i8* %"idx_ptr.5"
  ret void
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [29 x i8]* @"str_5" to i8*
  %".8" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"cls"()
  call void @"load_game"()
  %"running" = alloca i64
  store i64 1, i64* %"running"
  br label %"while_cond"
while_cond:
  %"running_load" = load i64, i64* %"running"
  %"icmp" = icmp eq i64 %"running_load", 1
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 4096)
  %"g_pc_load" = load i64, i64* @"g_pc"
  %".13" = getelementptr i8, i8* %"alloc_bytes_call", i64 %"g_pc_load"
  %"ptr_idx_load" = load i8, i8* %".13"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"shl" = shl i64 %"idx_sext", 8
  %"alloc_bytes_call.1" = call i8* @"GC_malloc"(i64 4096)
  %"g_pc_load.1" = load i64, i64* @"g_pc"
  %"add" = add i64 %"g_pc_load.1", 1
  %".14" = getelementptr i8, i8* %"alloc_bytes_call.1", i64 %"add"
  %"ptr_idx_load.1" = load i8, i8* %".14"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"bitor" = or i64 %"shl", %"idx_sext.1"
  %"opcode" = alloca i64
  store i64 %"bitor", i64* %"opcode"
  %"opcode_load" = load i64, i64* %"opcode"
  %"icmp.1" = icmp eq i64 %"opcode_load", 224
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  call void @"draw_screen"()
  %".46" = bitcast [18 x i8]* @"str_13" to i8*
  %".47" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".47", i8* %".46")
  %"alloc_bytes_call.5" = call i8* @"GC_malloc"(i64 16)
  %".48" = getelementptr i8, i8* %"alloc_bytes_call.5", i64 0
  %"ptr_idx_load.3" = load i8, i8* %".48"
  %"idx_sext.3" = sext i8 %"ptr_idx_load.3" to i64
  %".49" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".49")
  %".50" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".50", i64 %"idx_sext.3")
  %".51" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".51")
  %".52" = bitcast [21 x i8]* @"str_18" to i8*
  %".53" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".53", i8* %".52")
  %".54" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".54")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_then:
  call void @"cls"()
  %"g_pc_load.2" = load i64, i64* @"g_pc"
  %"add.1" = add i64 %"g_pc_load.2", 2
  store i64 %"add.1", i64* @"g_pc"
  br label %"if_end"
if_else:
  %"opcode_load.1" = load i64, i64* %"opcode"
  %"bitand" = and i64 %"opcode_load.1", 61440
  %"icmp.2" = icmp eq i64 %"bitand", 24576
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_end:
  %"g_pc_load.5" = load i64, i64* @"g_pc"
  %"icmp.4" = icmp sge i64 %"g_pc_load.5", 518
  br i1 %"icmp.4", label %"if_then.3", label %"if_else.3"
if_then.1:
  %"opcode_load.2" = load i64, i64* %"opcode"
  %"bitand.1" = and i64 %"opcode_load.2", 3840
  %"ashr" = ashr i64 %"bitand.1", 8
  %"x" = alloca i64
  store i64 %"ashr", i64* %"x"
  %"opcode_load.3" = load i64, i64* %"opcode"
  %"bitand.2" = and i64 %"opcode_load.3", 255
  %"nn" = alloca i64
  store i64 %"bitand.2", i64* %"nn"
  %"nn_load" = load i64, i64* %"nn"
  %"alloc_bytes_call.2" = call i8* @"GC_malloc"(i64 16)
  %"x_load" = load i64, i64* %"x"
  %"idx_ptr" = getelementptr i8, i8* %"alloc_bytes_call.2", i64 %"x_load"
  %"elem_trunc" = trunc i64 %"nn_load" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"g_pc_load.3" = load i64, i64* @"g_pc"
  %"add.2" = add i64 %"g_pc_load.3", 2
  store i64 %"add.2", i64* @"g_pc"
  br label %"if_end.1"
if_else.1:
  %"opcode_load.4" = load i64, i64* %"opcode"
  %"bitand.3" = and i64 %"opcode_load.4", 61440
  %"icmp.3" = icmp eq i64 %"bitand.3", 28672
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_end.1:
  br label %"if_end"
if_then.2:
  %"opcode_load.5" = load i64, i64* %"opcode"
  %"bitand.4" = and i64 %"opcode_load.5", 3840
  %"ashr.1" = ashr i64 %"bitand.4", 8
  %"x.1" = alloca i64
  store i64 %"ashr.1", i64* %"x.1"
  %"opcode_load.6" = load i64, i64* %"opcode"
  %"bitand.5" = and i64 %"opcode_load.6", 255
  %"nn.1" = alloca i64
  store i64 %"bitand.5", i64* %"nn.1"
  %"alloc_bytes_call.3" = call i8* @"GC_malloc"(i64 16)
  %"x_load.1" = load i64, i64* %"x.1"
  %".28" = getelementptr i8, i8* %"alloc_bytes_call.3", i64 %"x_load.1"
  %"ptr_idx_load.2" = load i8, i8* %".28"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %"nn_load.1" = load i64, i64* %"nn.1"
  %"add.3" = add i64 %"idx_sext.2", %"nn_load.1"
  %"alloc_bytes_call.4" = call i8* @"GC_malloc"(i64 16)
  %"x_load.2" = load i64, i64* %"x.1"
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_bytes_call.4", i64 %"x_load.2"
  %"elem_trunc.1" = trunc i64 %"add.3" to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"g_pc_load.4" = load i64, i64* @"g_pc"
  %"add.4" = add i64 %"g_pc_load.4", 2
  store i64 %"add.4", i64* @"g_pc"
  br label %"if_end.2"
if_else.2:
  %".32" = bitcast [21 x i8]* @"str_8" to i8*
  %".33" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"opcode_load.7" = load i64, i64* %"opcode"
  %".34" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".35", i64 %"opcode_load.7")
  %".36" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".36")
  store i64 0, i64* %"running"
  br label %"if_end.2"
if_end.2:
  br label %"if_end.1"
if_then.3:
  store i64 0, i64* %"running"
  br label %"if_end.3"
if_else.3:
  br label %"if_end.3"
if_end.3:
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [2 x i8] c"#\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [3 x i8] c"%s\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [29 x i8] c"Iniciando Emulador CHIP-8...\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [21 x i8] c"Opcode desconhecido:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [18 x i8] c"V0 (esperado 15):\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [21 x i8] c"Emulador finalizado.\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c"\0a\00"