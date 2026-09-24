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
  %".7" = bitcast [24 x i8]* @"str_0" to i8*
  call void @"InitWindow"(i64 800, i64 600, i8* %".7")
  %"ball_x" = alloca i64
  store i64 400, i64* %"ball_x"
  %"ball_y" = alloca i64
  store i64 300, i64* %"ball_y"
  %"speed_x" = alloca i64
  store i64 5, i64* %"speed_x"
  %"speed_y" = alloca i64
  store i64 5, i64* %"speed_y"
  br label %"while_cond"
while_cond:
  %"WindowShouldClose_call" = call i64 @"WindowShouldClose"()
  %"icmp" = icmp eq i64 %"WindowShouldClose_call", 0
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"ball_x_load" = load i64, i64* %"ball_x"
  %"speed_x_load" = load i64, i64* %"speed_x"
  %"add" = add i64 %"ball_x_load", %"speed_x_load"
  store i64 %"add", i64* %"ball_x"
  %"ball_y_load" = load i64, i64* %"ball_y"
  %"speed_y_load" = load i64, i64* %"speed_y"
  %"add.1" = add i64 %"ball_y_load", %"speed_y_load"
  store i64 %"add.1", i64* %"ball_y"
  %"ball_x_load.1" = load i64, i64* %"ball_x"
  %"icmp.1" = icmp sgt i64 %"ball_x_load.1", 800
  br i1 %"icmp.1", label %"or_end", label %"or_rhs"
while_end:
  call void @"CloseWindow"()
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
or_rhs:
  %"ball_x_load.2" = load i64, i64* %"ball_x"
  %"icmp.2" = icmp slt i64 %"ball_x_load.2", 0
  br label %"or_end"
or_end:
  %"or_result" = phi  i1 [1, %"while_body"], [%"icmp.2", %"or_rhs"]
  br i1 %"or_result", label %"if_then", label %"if_else"
if_then:
  %"speed_x_load.1" = load i64, i64* %"speed_x"
  %"neg" = sub i64 0, %"speed_x_load.1"
  store i64 %"neg", i64* %"speed_x"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"ball_y_load.1" = load i64, i64* %"ball_y"
  %"icmp.3" = icmp sgt i64 %"ball_y_load.1", 600
  br i1 %"icmp.3", label %"or_end.1", label %"or_rhs.1"
or_rhs.1:
  %"ball_y_load.2" = load i64, i64* %"ball_y"
  %"icmp.4" = icmp slt i64 %"ball_y_load.2", 0
  br label %"or_end.1"
or_end.1:
  %"or_result.1" = phi  i1 [1, %"if_end"], [%"icmp.4", %"or_rhs.1"]
  br i1 %"or_result.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"speed_y_load.1" = load i64, i64* %"speed_y"
  %"neg.1" = sub i64 0, %"speed_y_load.1"
  store i64 %"neg.1", i64* %"speed_y"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  call void @"BeginDrawing"()
  call void @"ClearBackground"(i64 4294967295)
  %".28" = bitcast [15 x i8]* @"str_1" to i8*
  call void @"DrawText"(i8* %".28", i64 300, i64 250, i64 20, i64 255)
  %".29" = bitcast [2 x i8]* @"str_2" to i8*
  %"ball_x_load.3" = load i64, i64* %"ball_x"
  %"ball_y_load.3" = load i64, i64* %"ball_y"
  call void @"DrawText"(i8* %".29", i64 %"ball_x_load.3", i64 %"ball_y_load.3", i64 20, i64 4278190335)
  call void @"EndDrawing"()
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare void @"InitWindow"(i64 %".1", i64 %".2", i8* %".3")

declare void @"CloseWindow"()

declare i64 @"WindowShouldClose"()

declare void @"BeginDrawing"()

declare void @"EndDrawing"()

declare void @"ClearBackground"(i64 %".1")

declare void @"DrawText"(i8* %".1", i64 %".2", i64 %".3", i64 %".4", i64 %".5")

@"str_0" = constant [24 x i8] c"Lumina Engine - 2D Game\00"
@"str_1" = constant [15 x i8] c"Lumina Engine!\00"
@"str_2" = constant [2 x i8] c"O\00"